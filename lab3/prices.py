#Handling the price data for symbols
from datetime import datetime
from typing import List, Tuple
import pandas as pd
import yfinance as yf
from preprocessing import preprocess_stock_data


from db_config import get_connection


#Get symbol from portfolio
def get_symbols_for_portfolio(pid: int) -> List[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT stock_symbol FROM portfolio_stocks WHERE portfolio_id=%s;", (pid,))
    symbols = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return symbols

#Download data from yahoo finance and converting it into data frame
def fetch_prices(symbols: List[str], start: str, end: str) -> pd.DataFrame:
    if not symbols:
        return pd.DataFrame(columns=["symbol", "dt", "open", "high", "low", "close", "volume"])
    if isinstance(symbols, str):
        symbols = [symbols]

    df = yf.download(symbols, start=start, end=end, auto_adjust=False, progress=False, threads=True)
    if df.empty:
        return pd.DataFrame(columns=["symbol", "dt", "open", "high", "low", "close", "volume"])

    rows = []

    if isinstance(df.columns, pd.MultiIndex):
        if {"Open", "High", "Low", "Close", "Volume"}.intersection(df.columns.get_level_values(0)):
            df = df.swaplevel(0, 1, axis=1)  
        syms_in_df = set(df.columns.get_level_values(0))
        for sym in [s for s in symbols if s in syms_in_df]:
            sub = df[sym].reindex(columns=["Open", "High", "Low", "Close", "Volume"])
            for idx, r in sub.dropna(how="all").iterrows():
                v = r["Volume"]
                rows.append([sym, idx.date(), r["Open"], r["High"], r["Low"], r["Close"],
                             int(v) if pd.notna(v) else None])
    else:
        # Single ticker: flat columns
        sym = symbols[0]
        sub = df.reindex(columns=["Open", "High", "Low", "Close", "Volume"])
        for idx, r in sub.dropna(how="all").iterrows():
            v = r["Volume"]
            rows.append([sym, idx.date(), r["Open"], r["High"], r["Low"], r["Close"],
                         int(v) if pd.notna(v) else None])

    return pd.DataFrame(rows, columns=["symbol", "dt", "open", "high", "low", "close", "volume"])


#Add stock info
def upsert_prices(df: pd.DataFrame) -> Tuple[int, int]:
    if df.empty:
        return (0, 0)

    conn = get_connection()
    cur = conn.cursor()
    inserted, updated = 0, 0

    for _, r in df.iterrows():
        cur.execute(
            "SELECT id FROM stock_prices WHERE stock_symbol=%s AND dt=%s;",
            (r["symbol"], r["dt"])
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE stock_prices
                   SET open_price=%s, high_price=%s, low_price=%s, close_price=%s, volume=%s
                 WHERE id=%s
                """,
                (r["open"], r["high"], r["low"], r["close"],
                 int(r["volume"]) if pd.notna(r["volume"]) else None,
                 row[0])
            )
            updated += 1
        else:
            cur.execute(
                """
                INSERT INTO stock_prices (stock_symbol, dt, open_price, high_price, low_price, close_price, volume)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (r["symbol"], r["dt"], r["open"], r["high"], r["low"], r["close"],
                 int(r["volume"]) if pd.notna(r["volume"]) else None)
            )
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    return (inserted, updated)

#Get the symbols and fetch relevant price data
def fetch_and_store_for_portfolio(pid: int, start: str, end: str) -> Tuple[int, int]:
    symbols = get_symbols_for_portfolio(pid)
    if not symbols:
        print("This portfolio has no stocks. Add some first.")
        return (0, 0)
    df = fetch_prices(symbols, start, end)
    if df.empty:
        print("No data returned (check dates or symbols).")
        return (0, 0)

    df = preprocess_stock_data(df)

    return upsert_prices(df[['symbol', 'dt', 'open', 'high', 'low', 'close', 'volume']])

    df = fetch_prices(symbols, start, end)
    if df.empty:
        print("No data returned (check dates or symbols).")
        return (0, 0)
    return upsert_prices(df)


#Read prices for portfolio fromm DB
def query_prices(symbol: str, start: str, end: str):
    sdt = datetime.strptime(start, "%Y-%m-%d").date()
    edt = datetime.strptime(end, "%Y-%m-%d").date()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT dt, open_price, high_price, low_price, close_price, volume
          FROM stock_prices
         WHERE stock_symbol=%s AND dt BETWEEN %s AND %s
         ORDER BY dt
        """,
        (symbol.upper().strip(), sdt, edt)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
