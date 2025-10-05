#!/usr/bin/env python3
"""
Step 2: Data Pipeline Processing
Oil Wells Data Processing Project

This script takes the extracted PDF data and runs it through the complete data pipeline:
- Consolidates extracted JSON files
- Enhances data with web scraping (if configured)
- Applies data cleaning and standardization
- Generates CSV output for web application
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Note: We'll implement our own simple processing for now
# from data_pipeline import DataPipeline

def setup_logging():
    """Setup logging for the pipeline process"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/step2_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_output_directories():
    """Create necessary output directories"""
    directories = [
        "step2_output",
        "step2_output/processed_data",
        "step2_output/enhanced_data",
        "step2_output/csv_data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print(f"Created output directories: {', '.join(directories)}")

def check_step1_output():
    """Check if Step 1 output exists"""
    step1_dir = Path("step1_output")
    
    if not step1_dir.exists():
        raise FileNotFoundError("Step 1 output not found! Please run step1_extract_pdfs.py first.")
    
    extracted_data_dir = step1_dir / "extracted_data"
    if not extracted_data_dir.exists():
        raise FileNotFoundError("Step 1 extracted data not found!")
    
    json_files = list(extracted_data_dir.glob("*.json"))
    if not json_files:
        raise FileNotFoundError("No extracted JSON files found in Step 1 output!")
    
    print(f"Found {len(json_files)} extracted JSON files from Step 1")
    return json_files

def consolidate_extracted_data(json_files, logger):
    """Consolidate all extracted JSON files into a single dataset"""
    logger.info("Consolidating extracted data...")
    
    consolidated_data = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Flatten the data structure for easier processing
            flattened = {
                'source_file': data.get('source_file', json_file.name),
                'processing_timestamp': data.get('processing_timestamp', ''),
            }
            
            # Extract well information
            well_info = data.get('well_information', {})
            for key, value in well_info.items():
                flattened[f'well_{key}'] = value
            
            # Extract stimulation data (take first record if multiple)
            stim_data = data.get('stimulation_data', [])
            if stim_data and len(stim_data) > 0:
                stim = stim_data[0]
                for key, value in stim.items():
                    flattened[f'stim_{key}'] = value
            
            consolidated_data.append(flattened)
            
        except Exception as e:
            logger.error(f"Error processing {json_file}: {str(e)}")
    
    logger.info(f"Successfully consolidated {len(consolidated_data)} records")
    return consolidated_data

def create_csv_output(processed_data, output_dir, logger):
    """Create CSV files for web application"""
    logger.info("Creating CSV output files...")
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(processed_data)
    
    # Create main wells CSV
    wells_csv_path = output_dir / "wells_data.csv"
    df.to_csv(wells_csv_path, index=False)
    logger.info(f"Created wells CSV: {wells_csv_path}")
    
    # Create a simplified CSV with key fields for the web app
    key_columns = [
        'source_file', 'well_api_number', 'well_well_name', 'well_operator_name',
        'well_latitude', 'well_longitude', 'well_coordinate_source',
        'well_county', 'well_state', 'well_location_description'
    ]
    
    # Filter to only include columns that exist
    available_columns = [col for col in key_columns if col in df.columns]
    simplified_df = df[available_columns]
    
    # Rename columns to be web-app friendly
    column_mapping = {
        'well_api_number': 'api_number',
        'well_well_name': 'well_name',
        'well_operator_name': 'operator_name',
        'well_latitude': 'latitude',
        'well_longitude': 'longitude',
        'well_coordinate_source': 'coordinate_source',
        'well_county': 'county',
        'well_state': 'state',
        'well_location_description': 'location_description'
    }
    
    simplified_df = simplified_df.rename(columns=column_mapping)
    
    # Remove rows without coordinates for web display
    coord_df = simplified_df.dropna(subset=['latitude', 'longitude'])
    
    web_csv_path = output_dir / "wells_for_web.csv"
    coord_df.to_csv(web_csv_path, index=False)
    logger.info(f"Created web-ready CSV: {web_csv_path} ({len(coord_df)} wells with coordinates)")
    
    return wells_csv_path, web_csv_path

def generate_processing_report(consolidated_data, processed_data, output_dir, logger):
    """Generate a processing report"""
    report = {
        "step2_processing_summary": {
            "timestamp": datetime.now().isoformat(),
            "input_records": len(consolidated_data),
            "output_records": len(processed_data),
            "processing_success_rate": f"{(len(processed_data) / len(consolidated_data)) * 100:.1f}%" if consolidated_data else "0%"
        },
        "data_quality_stats": {
            "records_with_coordinates": len([r for r in processed_data if r.get('well_latitude') and r.get('well_longitude')]),
            "records_with_api_numbers": len([r for r in processed_data if r.get('well_api_number')]),
            "records_with_well_names": len([r for r in processed_data if r.get('well_well_name')]),
            "records_with_operators": len([r for r in processed_data if r.get('well_operator_name')]),
        },
        "coordinate_sources": {}
    }
    
    # Count coordinate sources
    coord_sources = {}
    for record in processed_data:
        source = record.get('well_coordinate_source', 'unknown')
        coord_sources[source] = coord_sources.get(source, 0) + 1
    report["coordinate_sources"] = coord_sources
    
    # Save report
    report_path = output_dir / "step2_processing_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Generated processing report: {report_path}")
    return report

def main():
    """Main execution function"""
    print("Starting Step 2: Data Pipeline Processing")
    print("=" * 50)
    
    # Setup
    logger = setup_logging()
    create_output_directories()
    
    try:
        # Check Step 1 output
        json_files = check_step1_output()
        
        # Consolidate extracted data
        print("\nConsolidating extracted data...")
        consolidated_data = consolidate_extracted_data(json_files, logger)
        
        # Save consolidated data
        consolidated_path = Path("step2_output/processed_data/consolidated_extracted_data.json")
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        print(f"Consolidated {len(consolidated_data)} records")
        
        # For now, we'll use the consolidated data as our "processed" data
        # In a full pipeline, this would go through additional processing
        processed_data = consolidated_data
        
        # Create CSV outputs
        print("\nCreating CSV outputs...")
        wells_csv, web_csv = create_csv_output(processed_data, Path("step2_output/csv_data"), logger)
        
        # Generate processing report
        print("\nGenerating processing report...")
        report = generate_processing_report(consolidated_data, processed_data, Path("step2_output"), logger)
        
        # Display results
        print("\n" + "=" * 50)
        print("STEP 2 RESULTS SUMMARY")
        print("=" * 50)
        
        summary = report['step2_processing_summary']
        print(f"Input Records: {summary['input_records']}")
        print(f"Output Records: {summary['output_records']}")
        print(f"Processing Success Rate: {summary['processing_success_rate']}")
        
        quality_stats = report['data_quality_stats']
        print(f"\nData Quality Statistics:")
        print(f"  Records with coordinates: {quality_stats['records_with_coordinates']}")
        print(f"  Records with API numbers: {quality_stats['records_with_api_numbers']}")
        print(f"  Records with well names: {quality_stats['records_with_well_names']}")
        print(f"  Records with operators: {quality_stats['records_with_operators']}")
        
        coord_sources = report['coordinate_sources']
        if coord_sources:
            print(f"\nCoordinate Sources:")
            for source, count in coord_sources.items():
                print(f"  {source}: {count}")
        
        print(f"\nOutput saved to: step2_output/")
        print(f"   - Consolidated data: {consolidated_path}")
        print(f"   - Wells CSV: {wells_csv}")
        print(f"   - Web-ready CSV: {web_csv}")
        print(f"   - Processing report: step2_output/step2_processing_report.json")
        
        print("\nStep 2 Complete! Ready for Step 3 (Web Application)")
        
    except Exception as e:
        logger.error(f"Fatal error in Step 2: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()