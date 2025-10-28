# lab9 — PDF → Embeddings → FAISS → Conversational QA

This folder contains a single script `App_p2_openai_freequota.py` that implements a pipeline to:

1. Extract text from PDFs in `lab9/pdfs`
2. Chunk the text (500 chars, 50 overlap)
3. Create OpenAI embeddings for chunks and store them in a FAISS vectorstore
4. Build a conversational retrieval chain (LangChain ConversationalRetrievalChain + ConversationBufferMemory)
5. Run an interactive REPL to ask questions (type `exit` or `quit` to stop)

This README documents how to run the script, environment variables, and troubleshooting tips.

---

## Requirements

- Python 3.8+ (script was used with Python 3.12 in development)
- Recommended packages (install in a venv):

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r lab9/requirements.txt
```

If you don't have a `requirements.txt`, at minimum install:

```bash
python3 -m pip install langchain langchain-openai openai faiss-cpu PyPDF2 sentence-transformers requests
```

Note: `faiss-cpu` can be installed via pip on many platforms. If you run into build issues, consider using a Python distribution or environment manager that suits your system.

---

## Environment variables

Create a file `lab9/.env` (this script automatically loads it) or export the variables in your shell.

Required for submission / OpenAI-only runs:

- `OPENAI_API_KEY` — your OpenAI API key (required by the current submission-ready version). Example:

```text
OPENAI_API_KEY="sk-..."
```

How to create `lab9/.env`

You can create the `.env` file inside the `lab9` folder with any plain-text editor or from the command line.

Example using a heredoc (works in zsh/bash):

```bash
cat > lab9/.env <<'EOF'
OPENAI_API_KEY="sk-REPLACE_WITH_YOUR_KEY"
EOF
```

Example using a text editor (macOS):

```bash
open -a TextEdit lab9/.env
# then paste the lines and save
```

Or create it by echoing a single line (safer to use a quoted value):

```bash
echo 'OPENAI_API_KEY="sk-REPLACE_WITH_YOUR_KEY"' > lab9/.env
```

Important: Do not commit `lab9/.env` to version control. Keep it private.

Optional / alternative (not required for submission) — the repository contains HF and Azure code paths that can be re-enabled:

- `HF_API_KEY` — Hugging Face Inference API key, allows using HF embeddings (in newer versions of the script).
- `HF_EMBED_MODEL` — HF embedding model (default: `sentence-transformers/all-MiniLM-L6-v2`).
- `AZURE_OPENAI_ENDPOINT` — Azure OpenAI resource endpoint (e.g. `https://your-resource.openai.azure.com/`)
- `AZURE_OPENAI_KEY` — Azure API key
- `AZURE_EMBED_DEPLOYMENT` and `AZURE_CHAT_DEPLOYMENT` — Azure deployment names for embeddings/chat

Do NOT commit `.env` to source control.

Examples for Hugging Face and Azure variables

Hugging Face example entries for `lab9/.env`:

```text
HF_API_KEY="hf-REPLACE_WITH_YOUR_HF_KEY"
HF_EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

Azure OpenAI example entries for `lab9/.env`:

```text
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_KEY="REPLACE_WITH_YOUR_AZURE_KEY"
AZURE_EMBED_DEPLOYMENT="your-embed-deployment-name"
AZURE_CHAT_DEPLOYMENT="your-chat-deployment-name"
```

How to add these values to `lab9/.env` (single heredoc example with multiple keys):

```bash
cat > lab9/.env <<'EOF'
OPENAI_API_KEY="sk-REPLACE_WITH_YOUR_KEY"
HF_API_KEY="hf-REPLACE_WITH_YOUR_HF_KEY"
HF_EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_KEY="REPLACE_WITH_YOUR_AZURE_KEY"
AZURE_EMBED_DEPLOYMENT="your-embed-deployment-name"
AZURE_CHAT_DEPLOYMENT="your-chat-deployment-name"
EOF
```

Important: include only the credentials you have and keep the file private. Do not commit `lab9/.env` to version control.

---

## Usage examples

1) Quick extract + save chunks (no embeddings):

```bash
python3 lab9/data_collection_openai_api.py --pdf-dir lab9/pdfs --vectorstore lab9/faiss_openai --skip-embed --save-chunks
```

This will extract text, chunk it, and save `lab9/chunks.json`.

2) Small test run (embed only first 50 chunks to reduce cost):

```bash
# make sure OPENAI_API_KEY is set in lab9/.env or exported
python3 lab9/App_p2_openai_freequota.py --pdf-dir lab9/pdfs --vectorstore lab9/faiss_openai --sample 50
```

3) Full run (build embeddings for all chunks and enter REPL):

```bash
python3 lab9/App_p2_openai_freequota.py --pdf-dir lab9/pdfs --vectorstore lab9/faiss_openai
```

When the FAISS index is created the script will start an interactive REPL where you can ask questions. Type `exit` or `quit` to end.

---

## Notes about `--use-hf` and other fallbacks

- The submission-ready version of the script enforces `OPENAI_API_KEY` and uses OpenAI embeddings and chat.
- The repository retains code for Hugging Face and local `sentence-transformers` fallbacks (handy when OpenAI quota is limited). If you want to use HF or local embeddings, you can re-enable those branches in the script or set the appropriate env vars (`HF_API_KEY` or `sentence-transformers` installed locally).

Run with Hugging Face Inference API

- Ensure `HF_API_KEY` is set in `lab9/.env` and `HF_EMBED_MODEL` is optionally set to a model you have access to.
- Example command (embed first 50 chunks for testing):

```bash
python3 lab9/App_p2_openai_freequota.py --pdf-dir lab9/pdfs --vectorstore lab9/faiss_openai --use-hf --sample 50
```

- Notes:
	- The script will send batches of texts to the Hugging Face Inference API for embedding. If the selected HF model is gated or your token lacks permission, the API may return an error. In that case, switch to a different HF model or use the OpenAI/local path.

Run with Azure OpenAI

- Configure your Azure variables in `lab9/.env` (see examples above). In particular provide:
	- `AZURE_OPENAI_ENDPOINT` — your resource endpoint
	- `AZURE_OPENAI_KEY` — resource key
	- `AZURE_EMBED_DEPLOYMENT` — deployment name for embeddings
	- `AZURE_CHAT_DEPLOYMENT` — deployment name for chat

- Example command (embed first 50 chunks for testing):

```bash
python3 lab9/App_p2_openai_freequota.py --pdf-dir lab9/pdfs --vectorstore lab9/faiss_openai --sample 50
```

- Notes:
	- The script detects Azure configuration and uses Azure-compatible calls for embeddings and chat when `AZURE_OPENAI_ENDPOINT` and deployment names are provided.



