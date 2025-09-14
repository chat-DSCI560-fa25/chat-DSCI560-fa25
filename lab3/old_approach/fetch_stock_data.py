import yfinance as yf
import mysql.connector
from datetime import datetime

# MySQL connection setup
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dsci560@ADS",
    database="stock_db"
)
cursor = conn.cursor()

# List of stock symbols
stocks = ["AAPL", "MSFT", "GOOGL"]
start_date = "2023-01-01"
end_date = "2023-09-12"

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_prices (
    symbol VARCHAR(10),
    date DATE,
    open FLOAT,
    close FLOAT,
    high FLOAT,
    low FLOAT,
    volume BIGINT,
    PRIMARY KEY(symbol, date)
)
""")
conn.commit()

# Fetch data and insert into MySQL
for symbol in stocks:
    data = yf.download(symbol, start=start_date, end=end_date)
    for date, row in data.iterrows():
        cursor.execute(""" 
            INSERT INTO stock_prices (stock_symbol, date, open_price, close_price, high_price, low_price, volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            symbol,
            date.date(),
            float(row['Open']),
            float(row['Close']),
            float(row['High']),
            float(row['Low']),
            int(row['Volume'])
       ))
    conn.commit()
    print(f"{symbol} data inserted successfully.")

# Close connection
cursor.close()
conn.close()
