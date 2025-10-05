#!/usr/bin/env python3
"""
Step 1: Extract Data from PDFs
Oil Wells Data Processing Project
"""

import os
import sys
import json
from pathlib import Path
import logging
from datetime import datetime

# Import our enhanced PDF processor
from pdf_processor import EnhancedPDFProcessor

def setup_logging():
    """Setup logging for the extraction process"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/step1_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_output_directories():
    """Create necessary output directories"""
    directories = [
        "step1_output",
        "step1_output/extracted_data",
        "step1_output/failed_extractions",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print(f"Created output directories: {', '.join(directories)}")

def get_pdf_files():
    """Get list of all PDF files to process"""
    pdf_dir = Path("pdf_data")
    
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory '{pdf_dir}' not found!")
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{pdf_dir}'!")
    
    print(f"Found {len(pdf_files)} PDF files to process")
    return sorted(pdf_files)

def process_single_pdf(processor, pdf_file, logger):
    """Process a single PDF file and return extracted data"""
    try:
        logger.info(f"Processing: {pdf_file.name}")
        
        # Extract data using our enhanced processor
        extracted_data = processor.process_pdf(str(pdf_file))
        
        if extracted_data:
            # Add source file information
            extracted_data['source_file'] = pdf_file.name
            extracted_data['processing_timestamp'] = datetime.now().isoformat()
            
            # Save individual extraction result
            output_file = Path("step1_output/extracted_data") / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully processed: {pdf_file.name}")
            return extracted_data, None
        else:
            error_msg = f"No data extracted from {pdf_file.name}"
            logger.warning(error_msg)
            return None, error_msg
            
    except Exception as e:
        error_msg = f"Error processing {pdf_file.name}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def save_processing_summary(successful_extractions, failed_extractions, total_files, logger):
    """Save a summary of the processing results"""
    summary = {
        "processing_summary": {
            "timestamp": datetime.now().isoformat(),
            "total_files_processed": total_files,
            "successful_extractions": len(successful_extractions),
            "failed_extractions": len(failed_extractions),
            "success_rate": f"{(len(successful_extractions) / total_files) * 100:.1f}%"
        },
        "successful_files": [data['source_file'] for data in successful_extractions],
        "failed_files": [{"file": error["file"], "error": error["error"]} for error in failed_extractions],
        "statistics": {
            "wells_with_coordinates": len([d for d in successful_extractions if d.get('latitude') and d.get('longitude')]),
            "wells_with_geocoded_coordinates": len([d for d in successful_extractions if d.get('coordinate_source') == 'geocoded']),
            "wells_with_extracted_coordinates": len([d for d in successful_extractions if d.get('coordinate_source') == 'extracted'])
        }
    }
    
    # Save processing summary
    summary_file = Path("step1_output/processing_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Save consolidated data
    if successful_extractions:
        consolidated_file = Path("step1_output/consolidated_well_data.json")
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(successful_extractions, f, indent=2, ensure_ascii=False)
    
    # Save failed extractions details
    if failed_extractions:
        failed_file = Path("step1_output/failed_extractions/failed_details.json")
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_extractions, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Processing Summary saved to: {summary_file}")
    return summary

def main():
    """Main execution function"""
    print("Starting Step 1: PDF Data Extraction")
    print("=" * 50)
    
    # Setup
    logger = setup_logging()
    create_output_directories()
    
    try:
        # Get PDF files
        pdf_files = get_pdf_files()
        
        # Initialize processor
        logger.info("Initializing Enhanced PDF Processor...")
        processor = EnhancedPDFProcessor(pdf_folder="pdf_data", output_folder="step1_output/extracted_data")
        
        # Process all PDFs
        successful_extractions = []
        failed_extractions = []
        
        print(f"\nProcessing {len(pdf_files)} PDF files...")
        print("-" * 50)
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            
            extracted_data, error = process_single_pdf(processor, pdf_file, logger)
            
            if extracted_data:
                successful_extractions.append(extracted_data)
                print(f"    Success - Found well: {extracted_data.get('well_name', 'Unknown')}")
            else:
                failed_extractions.append({"file": pdf_file.name, "error": error})
                print(f"    Failed - {error}")
        
        # Generate summary
        print("\n" + "=" * 50)
        print("EXTRACTION RESULTS SUMMARY")
        print("=" * 50)
        
        summary = save_processing_summary(successful_extractions, failed_extractions, len(pdf_files), logger)
        
        # Display results
        stats = summary['processing_summary']
        print(f"Total Files Processed: {stats['total_files_processed']}")
        print(f"Successful Extractions: {stats['successful_extractions']}")
        print(f"Failed Extractions: {stats['failed_extractions']}")
        print(f"Success Rate: {stats['success_rate']}")
        
        coord_stats = summary['statistics']
        print(f"\nCoordinate Statistics:")
        print(f"  Wells with coordinates: {coord_stats['wells_with_coordinates']}")
        print(f"  Direct extraction: {coord_stats['wells_with_extracted_coordinates']}")
        print(f"  Geocoded coordinates: {coord_stats['wells_with_geocoded_coordinates']}")
        
        print(f"\nOutput saved to: step1_output/")
        print(f"   - Individual extractions: step1_output/extracted_data/")
        print(f"   - Consolidated data: step1_output/consolidated_well_data.json")
        print(f"   - Processing summary: step1_output/processing_summary.json")
        
        if failed_extractions:
            print(f"   - Failed extractions: step1_output/failed_extractions/")
        
        print("\nStep 1 Complete! Ready for Step 2 (Data Pipeline)")
        
    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
