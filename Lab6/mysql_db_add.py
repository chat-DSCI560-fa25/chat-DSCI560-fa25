import mysql.connector
from mysql.connector import errorcode
import os
import json
import argparse
import re

# --- Database Configuration ---
# Match this to your db_init.py and local MySQL setup
DB_NAME = 'oil_wells_db'
DB_CONFIG = {
    'user': 'webadmin',      # <-- CHANGE THIS IF NEEDED
    'password': 'admin',     # <-- CHANGE THIS IF NEEDED
    'host': 'localhost',
    'database': DB_NAME  # Connect directly to the database
}

# --- Helper Functions for Data Cleaning & Type Conversion ---

def clean_and_convert(value, target_type):
    """
    Safely converts a value to a target type (int, float) for DB insertion.
    Returns None if the value is None, empty, or cannot be converted.
    """
    if value is None or value == '':
        return None
    try:
        # Remove non-numeric characters except for decimal points and negative signs
        cleaned_val = re.sub(r'[^\d.-]', '', str(value))
        if cleaned_val == '':
            return None
        if target_type == 'int':
            # For integers, also remove decimal part if present
            return int(float(cleaned_val))
        if target_type == 'float':
            return float(cleaned_val)
    except (ValueError, TypeError):
        return None
    return value


def insert_data(cursor, file_path):
    """
    Processes a single JSON file and inserts its data into the database.
    """
    print(f"Processing file: {os.path.basename(file_path)}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    well_info = data.get('well_information', {})
    stim_data_list = data.get('stimulation_data', [])

    # --- Step 1: Validate and Insert Well Information ---
    api_number = well_info.get('api_number')

    # The API number is the primary key and cannot be NULL. Skip this file if it's missing.
    if not api_number:
        print(f"  ->   SKIPPING: `api_number` is missing. Cannot insert into database.\n")
        return False

    # Using INSERT IGNORE to avoid errors on duplicate API numbers
    sql_well = """
        INSERT IGNORE INTO well_information (
            api_number, well_name, operator_name, latitude, 
            longitude, datum, surface_hole_location
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    well_values = (
        api_number,
        well_info.get('well_name'),
        well_info.get('operator_name'),
        well_info.get('latitude'),
        well_info.get('longitude'),
        well_info.get('datum'),
        well_info.get('surface_hole_location')
    )

    try:
        cursor.execute(sql_well, well_values)
        if cursor.rowcount > 0:
            print(f"  -> Inserted well: {api_number}")
        else:
            print(f"  -> Well {api_number} already exists. Skipping well info insert.")

    except mysql.connector.Error as err:
        print(f"  -> ERROR inserting well {api_number}: {err}\n")
        return False

    # --- Step 2: Insert Stimulation Data (if any) ---
    if not stim_data_list:
        print("  -> No stimulation data to insert.\n")
        return True # Successful, just nothing to do

    sql_stim = """
        INSERT INTO stimulation_data (
            api_number, date_stimulated, stimulated_formation, top_ft, bottom_ft, 
            stimulation_stages, volume, volume_units, treatment_type, acid_percent, 
            lbs_proppant, max_pressure_psi, max_rate_bbls_min
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for record in stim_data_list:
        stim_values = (
            api_number,  # Foreign Key
            record.get('date_stimulated'), # Assuming DB can parse date strings or it's NULL
            record.get('stimulated_formation'),
            clean_and_convert(record.get('top_ft'), 'int'),
            clean_and_convert(record.get('bottom_ft'), 'int'),
            clean_and_convert(record.get('stimulation_stages'), 'int'),
            clean_and_convert(record.get('volume'), 'float'),
            record.get('volume_units'),
            record.get('treatment_type'),
            clean_and_convert(record.get('acid_percent'), 'float'),
            clean_and_convert(record.get('lbs_proppant'), 'int'), # BIGINT can be handled as int in Python
            clean_and_convert(record.get('max_pressure_psi'), 'int'),
            clean_and_convert(record.get('max_rate_bbls_min'), 'float')
        )
        try:
            cursor.execute(sql_stim, stim_values)
            print(f"  -> Inserted stimulation record for {api_number}")
        except mysql.connector.Error as err:
            print(f"  ->  ERROR inserting stimulation data for {api_number}: {err}")
    
    print("") # Newline for cleaner output
    return True


def main():
    parser = argparse.ArgumentParser(description="Load parsed well data from JSON files into a MySQL database.")
    parser.add_argument("input_dir", help="Directory containing the parsed JSON files.")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f" Error: Input directory not found at '{args.input_dir}'")
        return

    json_files = [f for f in os.listdir(args.input_dir) if f.endswith('.json')]
    if not json_files:
        print(f"No JSON files found in '{args.input_dir}'.")
        return

    cnx = None
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print(f"Successfully connected to database '{DB_NAME}'.\n")

        success_count = 0
        for filename in json_files:
            file_path = os.path.join(args.input_dir, filename)
            if insert_data(cursor, file_path):
                success_count += 1
        
        # Commit all the successful transactions
        cnx.commit()
        print("--- All changes have been committed to the database. ---")
        print(f"Successfully processed and inserted data from {success_count} of {len(json_files)} files.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Database Access Denied: Check your username and password in DB_CONFIG.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Database '{DB_NAME}' does not exist. Please run `db_init.py` first.")
        else:
            print(f"A database error occurred: {err}")
    finally:
        if cnx and cnx.is_connected():
            cursor.close()
            cnx.close()
            print("Database connection closed.")


if __name__ == '__main__':
    main()