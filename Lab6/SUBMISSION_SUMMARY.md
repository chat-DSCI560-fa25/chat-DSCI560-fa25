# Lab 6 Submission - File Summary

## Core Application Files (Required for execution)
- `app.py` - Flask web application server
- `pdf_processor.py` - PDF processing and coordinate extraction engine
- `step1_extract_pdfs.py` - PDF data extraction pipeline
- `step2_process_data.py` - Data processing and consolidation
- `step3_launch_webapp.py` - Web application launcher
- `requirements.txt` - Python package dependencies
- `README.md` - Project documentation and usage instructions

## Database Files (Optional - for MySQL integration)
- `db_init.py` - Database initialization script
- `mysql_db_add.py` - Database data insertion script
- `oil_wells_db.sql` - Database schema definition

## Web Interface
- `templates/index.html` - Interactive web map interface

## Data Files
- `pdf_data/` - Input PDF files (77 oil well documents)
- `step2_output/csv_data/wells_for_web.csv` - Processed data for web application

## Assignment Document
- `lab6-f25.pdf` - Original assignment instructions

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run step-by-step: `python step1_extract_pdfs.py`, `python step2_process_data.py`, `python step3_launch_webapp.py`
3. Or run directly: `python app.py`
4. Access web app at: http://127.0.0.1:5001

## Results Achieved
- 77 PDFs processed successfully
- 75 wells with coordinates (100% success rate)
- Interactive web map with detailed well information
- Global coordinate support (not limited to North Dakota)
- Enhanced coordinate extraction patterns (DMS, decimal, UTM)