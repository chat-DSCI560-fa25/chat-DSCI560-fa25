# Lab 6: Oil Wells PDF Processing and Web Application

This project implements a comprehensive oil wells data processing system as required for DSCI 560 Laboratory Assignment 6. The system processes oil well PDF documents to extract well information, coordinates, and production data, then displays the results in an interactive web application with mapping capabilities.

## Project Structure

```
lab6/
├── app.py                    # Flask web application
├── pdf_processor.py          # PDF processing and coordinate extraction
├── step1_extract_pdfs.py     # Step 1: Extract data from PDFs
├── step2_process_data.py     # Step 2: Process and consolidate data
├── step3_launch_webapp.py    # Step 3: Launch web application
├── db_init.py               # Database initialization
├── mysql_db_add.py          # Database operations
├── oil_wells_db.sql         # Database schema
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── SUBMISSION_SUMMARY.md    # Assignment summary
├── lab6-f25.pdf            # Assignment specification
├── templates/               # HTML templates
│   └── index.html          # Main web interface
└── pdf_data/               # Input PDF files (77 files)
```

## Features

### Part 1: Data Collection, Wrangling, and Munging
- PDF text extraction and parsing from 77 oil well documents
- Coordinate extraction (DMS, decimal, UTM formats)
- Geocoding for locations without direct coordinates
- Well information extraction (API numbers, names, operators)
- Stimulation data processing (pressure, proppant amounts)
- Database integration with MySQL

### Part 2: Web Access and Visualization
- Interactive web map with well location markers
- Detailed well information display in popups
- Production and stimulation data visualization
- Flask-based web server with RESTful API
- Responsive web interface

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For OCR functionality, install Tesseract:
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

## Usage

### Method 1: Step-by-step execution

1. **Extract data from PDFs:**
```bash
python step1_extract_pdfs.py
```

2. **Process and consolidate data:**
```bash
python step2_process_data.py
```

3. **Launch web application:**
```bash
python step3_launch_webapp.py
```

### Method 2: Direct web application

If you already have processed data:
```bash
python app.py
```

Access the web application at: http://127.0.0.1:5001

**Note:** The step-by-step method (Method 1) is recommended for first-time execution to generate the processed data files.

## Database Setup (Optional)

To set up MySQL database:

1. Create database:
```bash
mysql -u root -p < oil_wells_db.sql
```

2. Initialize database:
```bash
python db_init.py
```

3. Add data to database:
```bash
python mysql_db_add.py
```

## Data Processing Results

- Total PDFs processed: 77
- Successful extractions: 76 (98.7% success rate)
- Wells with coordinates: 76 (100% of successful extractions)
- Direct coordinate extraction: 67 wells
- Geocoded coordinates: 9 wells

## Technical Details

### Coordinate Extraction
- DMS format: 48° 2' 8.330 N, 103° 36' 11.190 W
- Decimal format: 48.109997, -103.603108
- UTM coordinates with zone information
- Global coordinate bounds support

### Web Application
- Flask backend with RESTful API
- Leaflet.js for interactive mapping
- Responsive design with well information popups
- Real-time coordinate validation

## Assignment Compliance

This implementation fulfills all requirements specified in the Laboratory Assignment 6 documentation:

### Part 1 Requirements
- PDF parsing and data extraction from oil well documents
- Database table creation and data storage (MySQL)
- Web scraping integration capabilities
- Data preprocessing and cleaning
- OCR functionality for text extraction

### Part 2 Requirements
- Interactive web-based mapping interface
- Push pin markers for well locations
- Detailed popup windows with well information
- Professional web interface design

## File Descriptions

- `pdf_processor.py`: Core PDF processing with enhanced coordinate extraction
- `app.py`: Flask web application with coordinate parsing and validation
- `step1_extract_pdfs.py`: Batch PDF processing pipeline
- `step2_process_data.py`: Data consolidation and CSV generation
- `step3_launch_webapp.py`: Web application launcher with configuration
- `templates/index.html`: Interactive map interface
- `db_init.py`: MySQL database initialization
- `mysql_db_add.py`: Database data insertion operations
- `oil_wells_db.sql`: Database schema definition