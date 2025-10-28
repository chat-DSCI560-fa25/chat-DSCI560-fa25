import os
# Disable TensorFlow (we only need PyTorch)
os.environ['USE_TF'] = '0'
os.environ['USE_TORCH'] = '1'

import streamlit as st
from datetime import datetime
from exec_model_cli import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain

# Page configuration
st.set_page_config(
    page_title="PDF Q&A Chatbot",
    page_icon="📚",
    layout="wide"
)

# Initialize session state variables
if 'conversation_chain' not in st.session_state:
    st.session_state.conversation_chain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

# Sidebar for PDF upload
with st.sidebar:
    st.title("📚 PDF Q&A Chatbot")
    st.markdown("---")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF files to ask questions about"
    )
    
    # Process button
    if st.button("Process PDFs", type="primary", use_container_width=True):
        if uploaded_files:
            with st.spinner("Processing PDFs... This may take a moment"):
                try:
                    # Create upload directory if it doesn't exist
                    upload_dir = "uploaded_pdfs"
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save uploaded files
                    pdf_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(upload_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        pdf_paths.append(file_path)
                    
                    # Extract text from PDFs
                    raw_text = get_pdf_text(pdf_paths)
                    
                    if not raw_text:
                        st.error("Could not extract text from PDFs")
                    else:
                        # Create text chunks
                        text_chunks = get_text_chunks(raw_text)
                        st.info(f"Split text into {len(text_chunks)} chunks")
                        
                        # Create vector store
                        vectorstore = get_vectorstore(text_chunks)
                        
                        # Create conversation chain
                        conversation_chain = get_conversation_chain(vectorstore)
                        
                        # Store in session state
                        st.session_state.conversation_chain = conversation_chain
                        st.session_state.processed_files = [f.name for f in uploaded_files]
                        
                        st.success(f"✅ Successfully processed {len(uploaded_files)} PDF(s)!")
                        
                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")
        else:
            st.warning("Please upload PDF files first")
    
    # Show processed files
    if st.session_state.processed_files:
        st.markdown("---")
        st.subheader("Processed Files:")
        for file in st.session_state.processed_files:
            st.text(f"📄 {file}")
    
    # Clear session button
    st.markdown("---")
    if st.button("Clear Session", use_container_width=True):
        st.session_state.conversation_chain = None
        st.session_state.chat_history = []
        st.session_state.processed_files = []
        st.rerun()
    
    # Info section
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This chatbot uses:
    - **Embeddings**: all-MiniLM-L6-v2
    - **Vector Store**: FAISS
    - **LLM**: Llama 2 (GGUF)
    """)

# Main chat interface
st.title("💬 Chat with your PDFs")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(message["question"])
    with st.chat_message("assistant"):
        st.write(message["answer"])

# Chat input
if prompt := st.chat_input("Ask a question about your PDFs"):
    # Check if PDFs have been processed
    if st.session_state.conversation_chain is None:
        st.warning("⚠️ Please upload and process PDF files first using the sidebar")
    else:
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.conversation_chain({'question': prompt})
                    answer = response['answer']
                    st.write(answer)
                    
                    # Save to chat history
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "question": prompt,
                        "answer": answer
                    })
                    
                except Exception as e:
                    st.error(f"Error processing question: {str(e)}")

# Show instructions if no PDFs processed yet
if st.session_state.conversation_chain is None:
    st.info("👈 Upload PDF files using the sidebar to get started!")

