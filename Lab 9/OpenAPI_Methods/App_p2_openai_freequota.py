"""
App_p2_openai_freequota.py
Part 2: Data Collection / Processing / Storage using OpenAI API (free/limited quota)
— Extract text from PDFs → chunk → embed (text-embedding-ada-002) → vector store (FAISS) → QA via gpt-3.5-turbo
"""

import os
import time
import argparse
import PyPDF2
import numpy as np
import faiss
import openai
import requests
from pathlib import Path
import json

# Optional local embeddings (sentence-transformers) — used when OpenAI quota is unavailable
_HAVE_LOCAL_EMBED = False
try:
    from sentence_transformers import SentenceTransformer
    _HAVE_LOCAL_EMBED = True
except Exception:
    _HAVE_LOCAL_EMBED = False


# Auto-load a local .env file (lab9/.env) if present so users can store OPENAI_API_KEY there
def _load_local_env():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('\"').strip("\'")
            # Only set the variable if it's not already in the environment
            if k and k not in os.environ and v:
                os.environ[k] = v
    except Exception:
        # never crash on env loading
        pass


# load lab9/.env if present
_load_local_env()

# Load optional key rotation file 'keys.txt' (one key per line) and set OPENAI_API_KEYS
def _load_keys_file():
    keys_path = Path(__file__).parent / "keys.txt"
    if not keys_path.exists():
        return
    try:
        keys = []
        for raw in keys_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            keys.append(line)
        if keys and "OPENAI_API_KEYS" not in os.environ:
            os.environ["OPENAI_API_KEYS"] = ",".join(keys)
    except Exception:
        pass

_load_keys_file()

# Azure OpenAI optional configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("OPENAI_API_BASE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_API_KEY")
AZURE_EMBED_DEPLOYMENT = os.getenv("AZURE_EMBED_DEPLOYMENT")
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT")
if AZURE_OPENAI_ENDPOINT:
    # configure openai client for Azure if endpoint is present
    try:
        openai.api_type = "azure"
        openai.api_base = AZURE_OPENAI_ENDPOINT.rstrip("/")
        # set a sensible default API version (can be overridden by env)
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-10-01")
        if AZURE_OPENAI_KEY:
            openai.api_key = AZURE_OPENAI_KEY
    except Exception:
        pass

# Hugging Face Inference API settings (optional)
HF_API_KEY = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
HF_EMBED_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# LangChain imports: try several common module paths so the script works across
# different langchain versions and small wrapper packages installed from PyPI.
try:
    # Preferred (modern) imports
    from langchain.text_splitter import CharacterTextSplitter
except Exception:
    try:
        # Older or alternate package layout
        from langchain.text_splitters import CharacterTextSplitter
    except Exception:
        try:
            # Fallback to the tiny wrapper package if present
            from langchain_text_splitters import CharacterTextSplitter
        except Exception:
            raise ImportError(
                "Cannot import CharacterTextSplitter. Install 'langchain' or 'langchain-text-splitters'."
            )

try:
    from langchain.vectorstores import FAISS
except Exception:
    try:
        from langchain_community.vectorstores import FAISS
    except Exception:
        raise ImportError(
            "Cannot import FAISS vectorstore. Install 'langchain' and/or 'langchain-community'."
        )

try:
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.chat_models import ChatOpenAI
except Exception:
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    except Exception:
        raise ImportError(
            "Cannot import OpenAIEmbeddings/ChatOpenAI. Install 'langchain' or 'langchain-openai'."
        )

# Import ConversationalRetrievalChain and ConversationBufferMemory with fallbacks
HAVE_CONVERSATIONAL_CHAIN = False
try:
    from langchain.chains import ConversationalRetrievalChain
    HAVE_CONVERSATIONAL_CHAIN = True
except Exception:
    try:
        from langchain.chains.conversational_retrieval import ConversationalRetrievalChain
        HAVE_CONVERSATIONAL_CHAIN = True
    except Exception:
        HAVE_CONVERSATIONAL_CHAIN = False

HAVE_CONVERSATIONAL_MEMORY = False
try:
    from langchain.memory import ConversationBufferMemory
    HAVE_CONVERSATIONAL_MEMORY = True
except Exception:
    try:
        from langchain.memory.conversation_buffer import ConversationBufferMemory
        HAVE_CONVERSATIONAL_MEMORY = True
    except Exception:
        HAVE_CONVERSATIONAL_MEMORY = False

# ---------- CONFIGuration ----------
_BASE_DIR = Path(__file__).parent
PDF_FOLDER = _BASE_DIR / "pdfs"                # folder containing your PDFs (resolved relative to script)
VECTORSTORE_PATH = _BASE_DIR / "faiss_openai"  # where to save/load FAISS index (resolved relative to script)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

EMBED_MODEL = "text-embedding-ada-002"   # Free‐tier eligible embedding model
CHAT_MODEL = "gpt-3.5-turbo"             # Free‐tier eligible chat model

# Optional: set a throttle to avoid hitting rate limit
THROTTLE_SECONDS = 1.0  # delay between API calls

# ---------- Check API Key ----------
# Require OPENAI_API_KEY (this script was written for the OpenAI API path).
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Use the environment variable only. Do NOT hard-code keys in source.
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- STEP 1: PDF TEXT Extraction ----------
def extract_text_from_pdfs(pdf_folder):
    all_text = ""
    p = Path(pdf_folder)
    if not p.exists():
        return all_text
    pdf_files = sorted([x for x in p.iterdir() if x.is_file() and x.suffix.lower() == ".pdf"])
    for path in pdf_files:
        fname = path.name
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                pages = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                print(f"[+] {fname}: extracted {len(pages)} pages")
                all_text += "\n".join(pages) + "\n"
        except Exception as e:
            print(f"[!] Failed {fname}: {e}")
    return all_text

# ---------- STEP 2: Chunking ----------
def chunk_text(text):
    splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        length_function = len
    )
    chunks = splitter.split_text(text)
    print(f"[+] Created {len(chunks)} chunks")
    return chunks

# ---------- STEP 3: Create or Load Vectorstore ----------
def create_or_load_vectorstore(chunks, persist_path=VECTORSTORE_PATH, sample_n: int = 0, use_hf: bool = False):
    p = Path(persist_path)
    if p.exists():
        try:
            print("[*] Loading existing FAISS vectorstore …")
            vs = FAISS.load_local(str(p), OpenAIEmbeddings(model=EMBED_MODEL))
            print("[+] Loaded persisted vectorstore")
            return vs
        except Exception as e:
            print(f"[!] Load failed ({e}), rebuilding…")
    # If use_hf is requested, try Hugging Face Inference API for embeddings first
    # (requires HF_API_KEY to be set in env or .env). Otherwise, try OpenAI and
    # fall back to local sentence-transformers if OpenAI fails.
    def _try_hf_embeddings(texts, batch_size=16, timeout=30):
        if not HF_API_KEY:
            raise RuntimeError("HF_API_KEY not set; cannot use Hugging Face Inference API")

        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        model = HF_EMBED_MODEL

        def embed_batch(batch_texts):
            url = f"https://api-inference.huggingface.co/embeddings/{model}"
            payload = {"inputs": batch_texts}
            # Optionally wait for model to load
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                resp.raise_for_status()
                data = resp.json()
                # data is typically a list of embedding vectors
                if isinstance(data, dict) and "error" in data:
                    raise RuntimeError(f"HF error: {data.get('error')}")
                # Some HF responses wrap embeddings under 'data' with 'embedding' keys
                if isinstance(data, dict) and "data" in data:
                    embs = [d.get("embedding") or d for d in data.get("data")]
                else:
                    embs = data
                return [list(map(float, e)) for e in embs]
            except Exception as e:
                raise

        all_embs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            print(f"[*] Sending batch {i//batch_size + 1} to Hugging Face ({len(batch)} items)")
            embs = embed_batch(batch)
            all_embs.extend(embs)
            time.sleep(0.1)
        return all_embs

    try:
        if use_hf:
            print("[*] --use-hf set: embedding chunks using Hugging Face Inference API …")
            if sample_n and int(sample_n) > 0:
                chunk_subset = chunks[: int(sample_n)]
            else:
                chunk_subset = chunks

            class HFEmbeddings:
                def embed_documents(self, texts):
                    return _try_hf_embeddings(texts)

            hf_embedder = HFEmbeddings()
            vs = FAISS.from_texts(texts=chunk_subset, embedding=hf_embedder)
            p.mkdir(parents=True, exist_ok=True)
            vs.save_local(str(p))
            print(f"[+] Saved vectorstore to {p} (Hugging Face embeddings)")
            return vs
    except Exception as e:
        print(f"[!] Hugging Face embeddings failed: {e}")

    # Try OpenAI embeddings first with retries/key rotation; if that fails due to
    # rate limits/quota, fall back to local sentence-transformers if available.
    def _try_openai_with_retries(texts, max_retries=3, backoff_base=2.0):
        # OPENAI_API_KEYS (optional) can provide comma-separated alternate keys
        keys = os.getenv("OPENAI_API_KEYS")
        key_list = [os.getenv("OPENAI_API_KEY")] if os.getenv("OPENAI_API_KEY") else []
        if keys:
            key_list = [k.strip() for k in keys.split(",") if k.strip()]

        attempts = 0
        last_err = None
        # Try rotating through keys and retrying with exponential backoff
        while attempts < max_retries:
            for k in (key_list or [None]):
                if k:
                    os.environ["OPENAI_API_KEY"] = k
                    openai.api_key = k
                print(f"[*] Attempting OpenAI embeddings (attempt {attempts+1}){' using alternate key' if k and k!=os.getenv('OPENAI_API_KEY') else ''}...")
                try:
                    # If Azure settings are provided, use an Azure-compatible embeddings wrapper
                    if AZURE_OPENAI_ENDPOINT and AZURE_EMBED_DEPLOYMENT:
                        class AzureEmbeddings:
                            def __init__(self, deployment):
                                self.deployment = deployment
                            def embed_documents(self, texts):
                                # Azure uses 'engine' param for embeddings
                                resp = openai.Embedding.create(engine=self.deployment, input=texts)
                                # response may contain data list with 'embedding'
                                embs = [d['embedding'] for d in resp['data']]
                                return [list(map(float, e)) for e in embs]
                        embedder = AzureEmbeddings(AZURE_EMBED_DEPLOYMENT)
                    else:
                        embedder = OpenAIEmbeddings(model=EMBED_MODEL)
                    vs = FAISS.from_texts(texts=texts, embedding=embedder)
                    return vs
                except Exception as e:
                    last_err = e
                    msg = str(e).lower()
                    # If it's a hard quota/insufficient_quota error, try the next key
                    if "insufficient_quota" in msg or "quota" in msg or "rate limit" in msg or isinstance(e, getattr(openai, 'RateLimitError', Exception)):
                        print(f"[!] OpenAI attempt failed (quota/rate): {e}")
                        # try next key immediately
                        continue
                    else:
                        # For other errors, backoff and retry
                        wait = backoff_base ** attempts
                        print(f"[!] OpenAI attempt failed: {e}. Backing off {wait:.1f}s and retrying...")
                        time.sleep(wait)
                        attempts += 1
                        continue
            # increment attempts if we cycled keys
            attempts += 1
        # If we exit loop, raise last exception
        if last_err:
            raise last_err
        raise RuntimeError("OpenAI embedding attempts failed")

    try:
        # If sample_n is provided, reduce the number of chunks to embed to conserve quota
        if sample_n and int(sample_n) > 0:
            print(f"[*] --sample set: embedding only the first {sample_n} chunks (of {len(chunks)})")
            chunk_subset = chunks[:int(sample_n)]
        else:
            chunk_subset = chunks

        print("[*] Embedding chunks using OpenAIEmbeddings (with retries) …")
        vs = _try_openai_with_retries(chunk_subset, max_retries=4)
    except Exception as e:
        print(f"[!] OpenAI embedding failed after retries: {e}")
        if _HAVE_LOCAL_EMBED:
            print("[*] Falling back to local SentenceTransformer embeddings …")
            local_model = SentenceTransformer("all-MiniLM-L6-v2")
            class LocalEmbeddings:
                def __init__(self, model):
                    self.model = model
                def embed_documents(self, texts):
                    embs = self.model.encode(texts, show_progress_bar=True)
                    return [list(map(float, e)) for e in embs]
            local_embedder = LocalEmbeddings(local_model)
            vs = FAISS.from_texts(texts=chunks, embedding=local_embedder)
        else:
            raise
    p.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(p))
    print(f"[+] Saved vectorstore to {p}")
    return vs

# ---------- STEP 4: Build Conversational Retrieval Chain ----------
def create_qa_chain(vectorstore):
    # If the LangChain ConversationalRetrievalChain is available, use it.
    if 'HAVE_CONVERSATIONAL_CHAIN' in globals() and HAVE_CONVERSATIONAL_CHAIN:
        chat_llm = ChatOpenAI(model_name=CHAT_MODEL, temperature=0.2)
        memory = None
        if 'HAVE_CONVERSATIONAL_MEMORY' in globals() and HAVE_CONVERSATIONAL_MEMORY:
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        if memory:
            qa = ConversationalRetrievalChain.from_llm(
                llm = chat_llm,
                retriever = vectorstore.as_retriever(search_kwargs={"k":3}),
                memory = memory,
                return_source_documents = True
            )
        else:
            qa = ConversationalRetrievalChain.from_llm(
                llm = chat_llm,
                retriever = vectorstore.as_retriever(search_kwargs={"k":3}),
                return_source_documents = True
            )
        return qa

    # Fallback implementation when ConversationalRetrievalChain is not available.
    def fallback_qa(input_dict):
        question = input_dict.get("question") if isinstance(input_dict, dict) else input_dict
        if not question:
            return {"answer": "", "source_documents": []}

        # Try to obtain a retriever from the vectorstore
        retriever = None
        try:
            if hasattr(vectorstore, "as_retriever"):
                retriever = vectorstore.as_retriever(search_kwargs={"k":3})
        except Exception:
            retriever = None

        docs = []
        if retriever is not None:
            if hasattr(retriever, "get_relevant_documents"):
                try:
                    docs = retriever.get_relevant_documents(question)
                except Exception:
                    docs = []
        # Last-resort: try vectorstore.similarity_search
        if not docs and hasattr(vectorstore, "similarity_search"):
            try:
                docs = vectorstore.similarity_search(question, k=3)
            except Exception:
                docs = []

        # Compose context from top docs
        context = "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)

        system = (
            "You are a helpful assistant. Use the provided context to answer the user's question. "
            "If the context does not contain the answer, say you don't know."
        )
        user_prompt = f"Context:\n{context}\n\nUser question: {question}\nAnswer concisely."

        # Call OpenAI chat completion directly as a simple fallback
        try:
            if AZURE_OPENAI_ENDPOINT and AZURE_CHAT_DEPLOYMENT:
                resp = openai.ChatCompletion.create(
                    engine=AZURE_CHAT_DEPLOYMENT,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
                    temperature=0.2,
                    max_tokens=512,
                )
            else:
                resp = openai.ChatCompletion.create(
                    model=CHAT_MODEL,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
                    temperature=0.2,
                    max_tokens=512,
                )
            answer = resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            answer = f"[Error calling OpenAI ChatCompletion: {e}]"

        return {"answer": answer, "source_documents": docs}

    return fallback_qa

# ---------- DRIVER Loop ----------
def main():
    parser = argparse.ArgumentParser(description="PDF -> FAISS -> OpenAI QA helper")
    parser.add_argument("--pdf-dir", type=str, help="Path to PDFs folder (overrides default)")
    parser.add_argument("--vectorstore", type=str, help="Path to vectorstore folder (overrides default)")
    parser.add_argument("--demo", action="store_true", help="Use demo sample text if no PDFs are present")
    parser.add_argument("--skip-embed", action="store_true", help="Run through chunking but skip embeddings/vectorstore creation (useful for testing)")
    parser.add_argument("--save-chunks", action="store_true", help="Save the chunked text to a JSON file (lab9/chunks.json) and exit when used with --skip-embed")
    parser.add_argument("--sample", type=int, default=0, help="If >0, embed only the first N chunks (conserves OpenAI quota)")
    parser.add_argument("--use-hf", action="store_true", help="Use Hugging Face Inference API for embeddings instead of OpenAI")
    args = parser.parse_args()

    pdf_folder = Path(args.pdf_dir) if args.pdf_dir else Path(PDF_FOLDER)
    vectorstore_path = Path(args.vectorstore) if args.vectorstore else Path(VECTORSTORE_PATH)
    sample_n = int(args.sample) if args.sample else 0

    # startup message
    print(f"[*] Using PDF folder: {pdf_folder}")
    print(f"[*] Using vectorstore path: {vectorstore_path}")
    if os.getenv("OPENAI_API_KEY"):
        masked = os.getenv("OPENAI_API_KEY")[:6] + "..." + os.getenv("OPENAI_API_KEY")[-4:]
        print(f"[*] OPENAI_API_KEY loaded (masked): {masked}")
    if HF_API_KEY:
        masked_hf = HF_API_KEY[:6] + "..." + HF_API_KEY[-4:]
        print(f"[*] HF_API_KEY loaded (masked): {masked_hf}")
    if args.use_hf:
        print("[!] --use-hf flag ignored: this run will use OpenAI embeddings only (per submission requirements)")

    print("[*] Step 1: Extracting text from PDFs …")
    text = extract_text_from_pdfs(pdf_folder)
    if not text.strip():
        if args.demo:
            print("[*] No PDFs found — using demo sample text.")
            text = (
                "Advanced Digital Systems - Installation Guide:\n"
                "This short demo document contains an overview of installation steps for the circuit design\n"
                "tool used in the course textbook. Follow the installer to set up the environment, then\n"
                "verify by running sample designs. The document also summarizes key commands and typical\n"
                "troubleshooting tips."
            )
        else:
            print("No text found. Exiting.")
            return

    print("[*] Step 2: Chunking text …")
    chunks = chunk_text(text)

    # Optionally save chunks to a JSON file for offline inspection
    if args.save_chunks:
        out_path = Path(__file__).parent / "chunks.json"
        try:
            out_path.write_text(json.dumps({"count": len(chunks), "chunks": chunks}, ensure_ascii=False), encoding="utf-8")
            print(f"[+] Saved {len(chunks)} chunks to {out_path}")
        except Exception as e:
            print(f"[!] Failed saving chunks to {out_path}: {e}")
        # If user wanted to only extract results, exit here when --skip-embed is also used
        if args.skip_embed:
            print("[*] --skip-embed set: extraction complete. Exiting.")
            return

    print("[*] Step 3: Create/load vectorstore …")
    if args.skip_embed:
        print("[*] --skip-embed set: skipping embeddings/vectorstore creation. Exiting after chunking.")
        return
    vectorstore = create_or_load_vectorstore(chunks, persist_path=vectorstore_path, sample_n=sample_n, use_hf=args.use_hf)

    print("[*] Step 4: Create QA chain …")
    qa_chain = create_qa_chain(vectorstore)

    print("\nChatbot ready. Type your question (or type 'exit' to quit):\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        # Delay to avoid hitting free-tier rate limits
        time.sleep(THROTTLE_SECONDS)
        result = qa_chain({"question": question})
        answer = result.get("answer") or ""
        print("\nBot:", answer.strip(), "\n")
        # Show sources
        srcs = result.get("source_documents")
        if srcs:
            print("Sources:")
            for i, doc in enumerate(srcs[:2]):
                snippet = doc.page_content[:200].replace("\n", " ").strip()
                print(f"  {i+1}: …{snippet}…")
            print("")
if __name__ == "__main__":
    main()
