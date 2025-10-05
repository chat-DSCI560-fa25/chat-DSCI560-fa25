import os
import subprocess
import time

# My paths
PDF_SOURCE_DIR = './pdfs'          # <-- There are 77 PDFs in this folder
JSON_OUTPUT_DIR = './json_output'   # <-- JSON files

def convert_pdfs_to_json():
    """
    I am using docling to convert all PDFs in a directory to JSON format with OCR,trying to 
    leverage the GPU.Expermenting with docling,I think this is something that can be used for the final project as well.
    """
    if not os.path.exists(PDF_SOURCE_DIR):
        print(f"Error: Source directory '{PDF_SOURCE_DIR}' not found.")
        print("Please create it and place your PDF files inside.")
        return

    os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(PDF_SOURCE_DIR) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    print(f"Found {total_files} PDF files to process.")

    for i, filename in enumerate(pdf_files):
        start_time = time.time()
        pdf_path = os.path.join(PDF_SOURCE_DIR, filename)
        json_filename = f"{os.path.splitext(filename)[0]}.json"
        json_path = os.path.join(JSON_OUTPUT_DIR, json_filename)
        
        print(f"\n[{i+1}/{total_files}] Processing: {filename}...")

        if os.path.exists(json_path):
            print(f"--> JSON file already exists. Skipping.")
            continue
            
        # Command to run docling with the Tesseract OCR engine
        command = [
            '.\\venv\\Scripts\\python.exe', '-m', 'docling',
            pdf_path,
            '--ocr-engine', 'tesseract',
            '--to', 'json',
            '--output', json_path
        ]
        
        try:
            # Execution
            subprocess.run(command, check=True, capture_output=True, text=True)
            end_time = time.time()
            print(f"--> Successfully converted to JSON in {end_time - start_time:.2f} seconds.")
        except subprocess.CalledProcessError as e:
            print(f"!!-- Error processing {filename} --!!")
            print(f"   Error: {e.stderr}")

if __name__ == '__main__':
    convert_pdfs_to_json()
    print("\nBatch conversion complete. You can now transfer the 'json_output' folder.")