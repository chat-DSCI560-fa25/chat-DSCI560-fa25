import mysql.connector
from mysql.connector import errorcode


DB_NAME = 'oil_wells_db'


DB_CONFIG = {
    'user': 'webadmin',        # <-- CHANGE THIS
    'password': 'admin',# <-- CHANGE THIS
    'host': 'localhost'
}


TABLES = {}

TABLES['well_information'] = (
    "CREATE TABLE `well_information` ("
    "  `api_number` VARCHAR(20) NOT NULL,"
    "  `well_name` VARCHAR(255),"
    "  `operator_name` VARCHAR(255),"
    "  `latitude` VARCHAR(50),"
    "  `longitude` VARCHAR(50),"
    "  `datum` VARCHAR(50),"
    "  `surface_hole_location` TEXT,"
    "  PRIMARY KEY (`api_number`)"
    ") ENGINE=InnoDB")

TABLES['stimulation_data'] = (
    "CREATE TABLE `stimulation_data` ("
    "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
    "  `api_number` VARCHAR(20),"
    "  `date_stimulated` DATE,"
    "  `stimulated_formation` VARCHAR(100),"
    "  `top_ft` INT,"
    "  `bottom_ft` INT,"
    "  `stimulation_stages` INT,"
    "  `volume` FLOAT,"
    "  `volume_units` VARCHAR(50),"
    "  `treatment_type` VARCHAR(100),"
    "  `acid_percent` FLOAT,"
    "  `lbs_proppant` BIGINT,"
    "  `max_pressure_psi` INT,"
    "  `max_rate_bbls_min` FLOAT,"
    "  `details` TEXT,"
    "  FOREIGN KEY (`api_number`) REFERENCES `well_information`(`api_number`)"
    ") ENGINE=InnoDB")


def setup_database():
    try:
        # Connect to the MySQL server
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("Successfully connected to MySQL server.")
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return

    try:
        # Create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{DB_NAME}' is ready.")
        cursor.execute(f"USE {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Failed to create database: {err}")
        exit(1)

    # Create the tables
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table `{table_name}`...", end='')
            # Using IF NOT EXISTS to make the script re-runnable
            cursor.execute(table_description.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS"))
            print(" OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(" already exists.")
            else:
                print(err.msg)
    
    
    cursor.close()
    cnx.close()
    print("\nDatabase setup is complete.")

if __name__ == '__main__':
    setup_database()