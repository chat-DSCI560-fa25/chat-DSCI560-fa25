import json
import re
import os
import argparse
from pprint import pprint

# ---Regex Patterns ---
PATTERNS = {
    "api_number": re.compile(r'API\s*#?[:\s]*(\d{2}-\d{3}-\d{5})'),
    "well_name": re.compile(r'Well\s*Name\s*[and\s*Number]*[:\s]*(.*)'),
    "operator_name": re.compile(r'Operator\s*[:\s]*(.*)'),
    "latitude": re.compile(r'Latitude\s*[:\s]*(.*)'),
    "longitude": re.compile(r'Longitude\s*[:\s]*(.*)'),
    "datum": re.compile(r'Datum\s*[:\s]*(.*)'),
    "surface_hole_location": re.compile(r'Surface\s*Hole\s*Location\s*\(SHL\)\s*[:\s]*(.*)')
}

def clean_value(value):
   
    if not value:
        return None
    return value.strip().split('\n')[0]

def extract_stimulation_data(doc):
    """
    Parses the stimulation data table from the docling JSON.
    """
    stimulation_records = []
    for table in doc.get('tables', []):
        header_text = ' '.join(cell.get('text', '') for cell in table.get('rows', [{}])[0].get('cells', [])).lower()
        if 'lbs proppant' in header_text and 'stimulated formation' in header_text:
            rows = table.get('rows', [])
            if len(rows) > 2:
                main_data = [cell.get('text', '') for cell in rows[1].get('cells', [])]
                treatment_data = [cell.get('text', '') for cell in rows[2].get('cells', [])]
                if len(main_data) >= 7 and len(treatment_data) >= 5:
                    record = {
                        'date_stimulated': clean_value(main_data[0]),
                        'stimulated_formation': clean_value(main_data[1]),
                        'top_ft': clean_value(main_data[2]),
                        'bottom_ft': clean_value(main_data[3]),
                        'stimulation_stages': clean_value(main_data[4]),
                        'volume': clean_value(main_data[5]),
                        'volume_units': clean_value(main_data[6]),
                        'treatment_type': clean_value(treatment_data[0]),
                        'acid_percent': clean_value(treatment_data[1]),
                        'lbs_proppant': clean_value(treatment_data[2]),
                        'max_pressure_psi': clean_value(treatment_data[3]),
                        'max_rate_bbls_min': clean_value(treatment_data[4]),
                    }
                    stimulation_records.append(record)
    return stimulation_records

def process_file(input_path, output_dir):

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            doc = json.load(f)
        
        full_text = '\n'.join(block['text'] for block in doc.get('texts', []))

        well_info = {}
        for key, pattern in PATTERNS.items():
            match = pattern.search(full_text)
            well_info[key] = clean_value(match.group(1)) if match else None

        stimulation_info = extract_stimulation_data(doc)
        
        final_output = {
            "well_information": well_info,
            "stimulation_data": stimulation_info
        }

        
        print(f"--- Processing {os.path.basename(input_path)} ---")
        pprint(final_output)
        
        # --- Save to JSON File ---
        base_filename = os.path.basename(input_path)
        filename_without_ext = os.path.splitext(base_filename)[0]
        output_filename = f"{filename_without_ext}_parsed.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=4)
            
        print(f"Saved parsed data to '{output_path}'\n")
        return True

    except Exception as e:
        print(f"Error processing file {os.path.basename(input_path)}: {e}\n")
        return False

def main():
    """
    Parses all JSON files
    """
    parser = argparse.ArgumentParser(description="Batch parse well data from JSON files in a directory.")
    parser.add_argument("input_dir", help="Path to the input directory containing JSON files.")
    parser.add_argument("output_dir", help="Directory to save the parsed output JSON files.")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory not found at '{args.input_dir}'")
        return

    
    os.makedirs(args.output_dir, exist_ok=True)

    
    json_files = [f for f in os.listdir(args.input_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in '{args.input_dir}'.")
        return

    print(f"Found {len(json_files)} JSON files to process.\n")
    success_count = 0
    
    
    for filename in json_files:
        input_path = os.path.join(args.input_dir, filename)
        if process_file(input_path, args.output_dir):
            success_count += 1
            
    print(f"--- Batch processing complete. ---")
    print(f"Successfully processed {success_count} of {len(json_files)} files.")

if __name__ == '__main__':
    main()