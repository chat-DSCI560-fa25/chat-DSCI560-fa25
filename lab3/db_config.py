#THis is a single file for db stuff
import mysql.connector

# THe below are details of db configuration local
DB_SETTINGS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "dsci",
    "password": "dsci", 
    "database": "stock_data",
}

#Establish connection using the details
def get_connection():
    return mysql.connector.connect(**DB_SETTINGS)
