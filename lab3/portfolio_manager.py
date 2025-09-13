import mysql.connector
import yfinance as yf

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dsci560@ADS",
    database="stock_db"
)
cursor = conn.cursor()

def add_portfolio(name):
    cursor.execute("INSERT INTO portfolios (portfolio_name) VALUES (%s)", (name,))
    conn.commit()
    print("Portfolio added successfully.")

def add_stock(portfolio_id, symbol):
    ticker = yf.Ticker(symbol)
    if ticker.info.get("shortName"):  # validation
        cursor.execute("INSERT INTO portfolio_stocks (portfolio_id, stock_symbol) VALUES (%s, %s)", (portfolio_id, symbol))
        conn.commit()
        print(f"{symbol} added successfully.")
    else:
        print("Invalid stock symbol.")

def remove_stock(portfolio_id, symbol):
    cursor.execute("DELETE FROM portfolio_stocks WHERE portfolio_id=%s AND stock_symbol=%s", (portfolio_id, symbol))
    conn.commit()
    print(f"{symbol} removed from portfolio.")

def show_portfolios():
    cursor.execute("SELECT * FROM portfolios")
    for portfolio in cursor.fetchall():
        print(f"Portfolio: {portfolio[1]}, Created on: {portfolio[2]}")
        cursor.execute("SELECT stock_symbol FROM portfolio_stocks WHERE portfolio_id=%s", (portfolio[0],))
        stocks = cursor.fetchall()
        print(" Stocks:", [s[0] for s in stocks])

# Example usage
add_portfolio("Tech Portfolio")
add_stock(1, "AAPL")
add_stock(1, "MSFT")
remove_stock(1, "MSFT")
show_portfolios()

cursor.close()
conn.close()
