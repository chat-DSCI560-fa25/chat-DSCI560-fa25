# This will initialize the db and create tables as defined below
import mysql.connector
from db_config import DB_SETTINGS

def main():
    #The below details are from our db_config file
    conn = mysql.connector.connect(
        host=DB_SETTINGS["host"],
        port=DB_SETTINGS["port"],
        user=DB_SETTINGS["user"],
        password=DB_SETTINGS["password"]
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS stock_data;")
    cur.close()
    conn.close()

    conn = mysql.connector.connect(**DB_SETTINGS)
    cur = conn.cursor()

    # Creating the following tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS portfolios (
        portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
        portfolio_name VARCHAR(120) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        portfolio_id INT NOT NULL,
        stock_symbol VARCHAR(20) NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_portfolio_symbol (portfolio_id, stock_symbol),
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
          ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_symbol VARCHAR(20) NOT NULL,
        dt DATE NOT NULL,
        open_price DOUBLE,
        high_price DOUBLE,
        low_price DOUBLE,
        close_price DOUBLE,
        volume BIGINT,
        UNIQUE KEY uq_symbol_dt (stock_symbol, dt)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("The specified tables have been created.")

if __name__ == "__main__":
    main()
