#This folder contains gui for uploading pdf and perfomring operations.
# PDF Q&A Chatbot - Lab 9

This project implements a Q&A chatbot over PDFs using open-source embeddings and LLMs. You have both a CLI version and a Web Interface.

## Prerequisites
- Python 3.8+
- Model file placed at `models/llama-2-7b-chat.Q4_K_M.gguf`
- Install deps: `pip install -r requirements.txt`

## Option A: Run the Streamlit Web Interface (RECOMMENDED!)
1. Start:
   - macOS/Linux: `./run_streamlit.sh`
   - Windows: `run_streamlit.bat`
   - Or: `streamlit run streamlit_app.py`
2. Open: http://localhost:8501 (opens automatically)
3. In the browser:
   - Upload one or more PDFs using sidebar
   - Click "Process PDFs"
   - Ask questions in the chat

## Option B: Run the CLI
1. Put PDFs in `pdf_files/`
2. Run: `python exec_model_cli.py`
3. Type questions (type `exit` to quit)

## Notes
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Vector store: FAISS (local)
- LLM: Llama 2 (GGUF via llama-cpp-python)

## Why Streamlit? (NEW!)
The Streamlit version offers several advantages:
- 55% less code - single file vs multiple files
- Modern chat UI out of the box
- Easier to develop and maintain
- No HTML/CSS/JS needed - pure Python!
- See STREAMLIT_COMPARISON.md for detailed comparison

## Troubleshooting
- If import errors: `pip install -r requirements.txt`
- If model not found: ensure `models/llama-2-7b-chat.Q4_K_M.gguf` exists
- If port 8501 busy: Streamlit will auto-select next available port
