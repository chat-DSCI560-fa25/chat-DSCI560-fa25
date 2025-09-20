# app/db_config.py
import os
import mysql.connector

def _env(k, d=None): 
    v = os.environ.get(k)
    return v if v not in (None, "") else d

DB_SETTINGS = {
    "host": _env("MYSQL_HOST", "db"),         
    "port": int(_env("MYSQL_PORT", "3306")),
    "user": _env("MYSQL_USER", "lab4user"),
    "password": _env("MYSQL_PASSWORD", "lab4pass"),
    "database": _env("MYSQL_DATABASE", "lab4db"),
}

def get_connection():
    return mysql.connector.connect(**DB_SETTINGS)
