# init_db.py
# Initializes the MySQL schema for Lab 3 + Lab 4 (sessions & results).
# Uses only MySQL tables; JSON is NOT used for storage here except where noted.

import mysql.connector
from db_config import DB_SETTINGS

DB_NAME = DB_SETTINGS.get("database", "stock_data")

DDL = [
    f"CREATE DATABASE IF NOT EXISTS {DB_NAME};",
    f"USE {DB_NAME};",

   
    # 1) The Portfolios Table
    """
    CREATE TABLE IF NOT EXISTS portfolios (
        portfolio_id   INT AUTO_INCREMENT PRIMARY KEY,
        portfolio_name VARCHAR(120) NOT NULL UNIQUE,
        created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # 2) The Portfolio_Stocks table
    """
    CREATE TABLE IF NOT EXISTS portfolio_stocks (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        portfolio_id  INT NOT NULL,
        stock_symbol  VARCHAR(20) NOT NULL,
        added_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_portfolio_symbol (portfolio_id, stock_symbol),
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
          ON DELETE CASCADE
    );
    """,

    # 3) The Strategy table
    """
    CREATE TABLE IF NOT EXISTS strategies (
        strategy_id  INT AUTO_INCREMENT PRIMARY KEY,
        name         VARCHAR(80) NOT NULL,      
        params_json  JSON NOT NULL,             
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # 5) Sessions Table for a backtest attempt 
    """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
        portfolio_id   INT NOT NULL,
        strategy_id    INT NOT NULL,
        start_date     DATE NOT NULL,
        end_date       DATE NOT NULL,
        initial_cash   DOUBLE NOT NULL,
        status         ENUM('draft','locked') NOT NULL DEFAULT 'draft',
        notes          VARCHAR(255) NULL,
        created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        locked_at      TIMESTAMP NULL,

        snapshot_mode  ENUM('reference','copied') NOT NULL DEFAULT 'reference',
        snapshot_info  JSON NULL,

        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
        FOREIGN KEY (strategy_id)  REFERENCES strategies(strategy_id)  ON DELETE RESTRICT,
        INDEX idx_session_portfolio (portfolio_id, start_date, end_date)
    );
    """,

    # 6) This is not being used kept for experimental purpose
    """
    CREATE TABLE IF NOT EXISTS session_prices (
        id            BIGINT AUTO_INCREMENT PRIMARY KEY,
        session_id    BIGINT NOT NULL,
        stock_symbol  VARCHAR(20) NOT NULL,
        dt            DATE NOT NULL,
        fields_json   JSON NOT NULL,      
        UNIQUE KEY uq_session_sym_dt (session_id, stock_symbol, dt),
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
        INDEX idx_session_sym_dt (session_id, stock_symbol, dt)
    );
    """,

    # 7) The session trades
    """
    CREATE TABLE IF NOT EXISTS session_trades (
        id           BIGINT AUTO_INCREMENT PRIMARY KEY,
        session_id   BIGINT NOT NULL,
        dt           DATE NOT NULL,                 
        stock_symbol VARCHAR(20) NOT NULL,
        side         ENUM('BUY','SELL') NOT NULL,
        price        DOUBLE NOT NULL,
        shares       INT NOT NULL,
        fees         DOUBLE DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
        INDEX idx_trades_session_dt (session_id, dt),
        INDEX idx_trades_symbol_dt (stock_symbol, dt)
    );
    """,


    # 8) The session metrics
    """
    CREATE TABLE IF NOT EXISTS session_metrics (
        session_id        BIGINT PRIMARY KEY,
        total_return      DOUBLE NULL,
        annualized_return DOUBLE NULL,
        sharpe            DOUBLE NULL,
        max_drawdown      DOUBLE NULL,
        trades_count      INT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    );
    """
]

def main():
    # 1) Connect without DB to ensure it exists
    root = mysql.connector.connect(
        host=DB_SETTINGS["host"],
        port=DB_SETTINGS["port"],
        user=DB_SETTINGS["user"],
        password=DB_SETTINGS["password"],
    )
    cur = root.cursor()
    cur.execute(DDL[0])  # CREATE DATABASE
    cur.close()
    root.close()

    # 2) Connect to the DB and run all DDL
    conn = mysql.connector.connect(**DB_SETTINGS)
    cur = conn.cursor()
    for stmt in DDL[1:]:
        cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()
    print("Database and tables are ready (Lab3 + Lab4 sessions).")

if __name__ == "__main__":
    main()
