#All the imports
import os
# Disable TensorFlow (we only need PyTorch)
os.environ['USE_TF'] = '0'
os.environ['USE_TORCH'] = '1'

import glob
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter 
from langchain_huggingface.embeddings import HuggingFaceEmbeddings 
from langchain_community.llms import LlamaCpp 
from langchain_community.vectorstores import FAISS 
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain

#Helper Functions referenced from app file

#Extracts text from a list of PDF file paths.
def get_pdf_text(pdf_paths):
  
    text = ""
    for pdf_path in pdf_paths:
        try:
            # Open the file in binary read mode
            with open(pdf_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            print(f"Successfully read {pdf_path}")
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
    return text

#Splits text into chunks
def get_text_chunks(text):
   
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,  
        chunk_overlap=100, 
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

#Creates a vector store from text chunks using local embeddings.
def get_vectorstore(text_chunks):
   

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")
  
    
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

#Creates a conversation chain using the local LlamaCpp model.
def get_conversation_chain(vectorstore):
 
    llm = LlamaCpp(
        model_path="models/llama-2-7b-chat.Q4_K_M.gguf",  #llama-2-7b-chat.ggmlv3.q4_1.bin
        n_ctx=1024, 
        n_batch=512,
        n_gpu_layers=32,  # Offload all layers to GPU for faster inference on M1 Pro
        f16_kv=True,      # Use 16-bit precision for faster GPU operations
        verbose=True      # Show progress during inference
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 2}),  # Reduced from 4 to 2 for faster processing
        memory=memory,
    )
    return conversation_chain




def main_driver():
    """
    Main driver function that runs the command-line chatbot.
    """
    
    load_dotenv()
    pdf_folder_path = "pdf_files" 
    
    if not os.path.isdir(pdf_folder_path):
        print(f"Error: Folder '{pdf_folder_path}' not found.")
        print("Please create this folder and add your PDF files to it.")
        return

   
    pdf_paths = glob.glob(os.path.join(pdf_folder_path, "*.pdf"))
    
    if not pdf_paths:
        print(f"No PDF files found in '{pdf_folder_path}'.")
        return

    print(f"Found {len(pdf_paths)} PDFs. Processing...")


    
    # Extract text
    raw_text = get_pdf_text(pdf_paths)
    if not raw_text:
        print("No text was extracted from the PDFs. Exiting.")
        return
        
    # Get text chunks
    text_chunks = get_text_chunks(raw_text)
    print(f"Split text into {len(text_chunks)} chunks.")

    #Create vector store
    print("Creating vector store... (This may take a moment to download the model)")
    vectorstore = get_vectorstore(text_chunks)
    print("Vector store created successfully.")

    # Create conversation chain
    print("Loading local LLM... (This may take a moment)")
    conversation_chain = get_conversation_chain(vectorstore)
    print("Conversation chain created. You can now ask questions.")
    
    #Start Question Loop 
    
    while True:
        # Get question from user
        user_question = input("\nAsk a question (or type 'exit' to quit): ")
        
        # Check if the user wants to quit
        if user_question.lower() == 'exit':
            print("Exiting chatbot. Goodbye!")
            break
        
        if not user_question.strip():
            continue
            
        # Run the question
        try:
            print("Thinking...")
            response = conversation_chain({'question': user_question})
            
            # Print the response 
            print(f"\nBot: {response['answer']}")
            
        except Exception as e:
            print(f"An error occurred while processing your question: {e}")


#Run driver function

if __name__ == '__main__':
    main_driver()