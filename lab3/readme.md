# Stock Portfolio Management System

A Python-based command-line application for managing stock portfolios, fetching market data, and storing information in a MySQL database.  
The system provides tools for creating and managing portfolios, adding/removing stocks, fetching historical price data via **yfinance**, and querying stored results.

---

## Project Structure

- **db_config.py**  
  Contains MySQL connection settings (`host`, `port`, `user`, `password`, `database`) and a helper function `get_connection()` for establishing database connections.

- **init_db.py**  
  Initializes the MySQL schema and creates required tables:
  - `portfolios` – portfolio metadata  
  - `portfolio_stocks` – stocks associated with portfolios  
  - `stock_prices` – daily OHLCV (Open, High, Low, Close, Volume) price data  

- **portfolio.py**  
  CLI utility for portfolio management (create, list portfolios).

- **stocks.py**  
  CLI utility for managing stocks inside a portfolio (add, remove, list).

- **prices.py**  
  Functions for:
  - Fetching historical data with **yfinance**  
  - Inserting/updating stock prices in MySQL  
  - Querying price data by symbol and/or date range  

- **main.py**  
  Central entry point with a menu-driven interface to access:
  - Portfolio Manager  
  - Stock Manager  
  - Price Fetcher  
  - Query Tools  

---

## Database Setup

1. Ensure **MySQL server** is running.
2. Create the database and user (if not already included in `init_db.py`):

   ```sql
   CREATE DATABASE stock_data;
   CREATE USER 'dsci'@'localhost' IDENTIFIED BY 'dsci';
   GRANT ALL PRIVILEGES ON stock_data.* TO 'dsci'@'localhost';
   FLUSH PRIVILEGES;
