#!/usr/bin/env python3
"""
Step 3: Web Application Launch
Oil Wells Data Processing Project

This script launches the Flask web application using processed data from Steps 1 & 2.
The application provides an interactive map visualization of oil well data.
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime

def setup_logging():
    """Setup logging for the web application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/step3_webapp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def check_prerequisites():
    """Check if previous steps have been completed"""
    logger = logging.getLogger(__name__)
    
    # Check Step 1 output
    step1_dir = Path("step1_output")
    if not step1_dir.exists():
        raise FileNotFoundError("Step 1 output not found! Please run step1_extract_pdfs.py first.")
    
    # Check Step 2 output
    step2_dir = Path("step2_output")
    if not step2_dir.exists():
        raise FileNotFoundError("Step 2 output not found! Please run step2_process_data.py first.")
    
    # Check for web-ready CSV
    web_csv = step2_dir / "csv_data" / "wells_for_web.csv"
    if not web_csv.exists():
        raise FileNotFoundError(f"Web-ready CSV not found at {web_csv}")
    
    logger.info("All prerequisites met")
    logger.info(f"Web data found: {web_csv}")
    return web_csv

def update_flask_app_config(web_csv_path):
    """Update Flask app configuration to use our processed data"""
    logger = logging.getLogger(__name__)
    
    # Read the current app.py file
    app_file = Path("app.py")
    if not app_file.exists():
        raise FileNotFoundError("Flask app.py not found!")
    
    # Update the CSV file configuration
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Find the POSSIBLE_CSV_FILES configuration
    if "POSSIBLE_CSV_FILES" in content:
        # Add our web CSV to the top of the list
        new_csv_config = f'''POSSIBLE_CSV_FILES = [
    "{web_csv_path}",  # Step 2 processed data
    "geocoding_demo/enhanced_wells_with_geocoding.csv",
    "pipeline_output/processed_data/consolidated_well_data.csv",
    "well_information.csv",
    "consolidated_well_data.csv"
]'''
        
        # Replace the configuration
        import re
        pattern = r'POSSIBLE_CSV_FILES = \[.*?\]'
        updated_content = re.sub(pattern, new_csv_config, content, flags=re.DOTALL)
        
        # Write back the updated content
        with open(app_file, 'w') as f:
            f.write(updated_content)
        
        logger.info(f"Updated Flask app to use: {web_csv_path}")
    else:
        logger.warning("Could not find POSSIBLE_CSV_FILES in app.py - using default configuration")

def display_startup_info(web_csv_path):
    """Display startup information"""
    logger = logging.getLogger(__name__)
    
    # Get statistics from the CSV
    import csv
    
    try:
        with open(web_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        total_wells = len(rows)
        wells_with_coords = len([r for r in rows if r.get('latitude') and r.get('longitude')])
        
        extracted_coords = len([r for r in rows if r.get('coordinate_source') == 'extracted'])
        geocoded_coords = len([r for r in rows if r.get('coordinate_source') == 'geocoded'])
        
        print("\n" + "=" * 60)
        print("OIL WELLS INTERACTIVE MAP - READY TO LAUNCH")
        print("=" * 60)
        print(f"Data Summary:")
        print(f"   Total wells in dataset: {total_wells}")
        print(f"   Wells with coordinates: {wells_with_coords}")
        print(f"   Direct extraction: {extracted_coords}")
        print(f"   Geocoded coordinates: {geocoded_coords}")
        
        print(f"\nWeb Application Features:")
        print(f"   Interactive map with well markers")
        print(f"   Detailed well information popups")
        print(f"   Coordinate source indicators")
        print(f"   Production and stimulation data display")
        
        print("\nStarting Flask development server...")
        print(f"   Data source: {web_csv_path}")
        print(f"   Access URL: http://127.0.0.1:5001")
        print(f"   Logs: logs/step3_webapp_*.log")
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"Error reading CSV statistics: {str(e)}")
        print(f"\nStarting Flask application with {web_csv_path}")

def launch_flask_app():
    """Launch the Flask application"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import and run the Flask app
        print("\nLaunching Flask application...")
        logger.info("Starting Flask application")
        
        # Import the Flask app
        import app
        
        # Run the Flask app
        app.app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=False  # Prevent double startup in debug mode
        )
        
    except KeyboardInterrupt:
        print("\n\nWeb application stopped by user")
        logger.info("Flask application stopped by user")
    except Exception as e:
        logger.error(f"Error starting Flask application: {str(e)}")
        print(f"Error starting web application: {str(e)}")
        sys.exit(1)

def main():
    """Main execution function"""
    print("Starting Step 3: Web Application Launch")
    print("=" * 50)
    
    # Setup
    logger = setup_logging()
    
    try:
        # Check prerequisites
        print("Checking prerequisites...")
        web_csv_path = check_prerequisites()
        
        # Update Flask app configuration
        print("Configuring web application...")
        update_flask_app_config(web_csv_path)
        
        # Display startup information
        display_startup_info(web_csv_path)
        
        # Launch Flask app
        launch_flask_app()
        
    except Exception as e:
        logger.error(f"Fatal error in Step 3: {str(e)}")
        print(f"Error: {str(e)}")
        print("\nMake sure you have completed:")
        print("   1. Step 1: python step1_extract_pdfs.py")
        print("   2. Step 2: python step2_process_data.py")
        sys.exit(1)

if __name__ == "__main__":
    main()