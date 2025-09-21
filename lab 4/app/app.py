from __future__ import annotations
from datetime import date
from math import floor
import re
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, jsonify, render_template, request,Response
import mysql.connector
import os
import pyarrow.parquet as pq
from backtest import fetch_and_store_prices
from strategies import sma,consensus,ema_rsi
import engine

#env-based config (MYSQL_HOST, MYSQL_DB, etc.)
from db_config import get_connection


app = Flask(__name__)

# tiny DB helpers 
def _all(sql: str, params=()):
    cn = get_connection(); cur = cn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); cn.close()
    return rows

def _one(sql: str, params=()):
    cn = get_connection(); cur = cn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close(); cn.close()
    return row

def _exec(sql: str, params=(), multi=False): 
    cn = get_connection(); cur = cn.cursor()
    if multi:
      for result in cur.execute(sql, params, multi=True): pass
    else:
      cur.execute(sql, params)
    cn.commit()
    last_id = cur.lastrowid
    cur.close(); cn.close()
    return last_id

# Different Pages 
@app.route("/")
def index():
    return render_template("index.html")

@app.get("/portfolio/<int:pid>")
def portfolio_page(pid: int):
    row = _one("SELECT portfolio_name FROM portfolios WHERE portfolio_id=%s", (pid,))
    if not row:
        return "Portfolio not found", 404
    return render_template("portfolio.html", pid=pid, pname=row[0])

# Portfolio CRUD 
@app.get("/api/portfolios")
def api_portfolios():
    from db_config import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT portfolio_id, portfolio_name FROM portfolios ORDER BY portfolio_id DESC;")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"id": pid, "name": name} for (pid, name) in rows])

@app.post("/api/portfolio")
def api_portfolio_create():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    try:
        pid = _exec("INSERT INTO portfolios(portfolio_name) VALUES (%s)", (name,))
        return jsonify({"id": pid, "name": name})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 409

@app.delete("/api/portfolio/<int:pid>")
def api_portfolio_delete(pid: int):
    _exec("DELETE FROM portfolios WHERE portfolio_id=%s", (pid,))
    return jsonify({"ok": True})

# Stocks per portfolio 
@app.get("/api/portfolio/<int:pid>/stocks")
def api_stocks_list(pid: int):
    rows = _all("""
        SELECT stock_symbol, added_at
          FROM portfolio_stocks
         WHERE portfolio_id=%s
         ORDER BY added_at DESC, stock_symbol ASC
    """, (pid,))
    return jsonify([
        {"symbol": r[0], "added_at": (r[1].isoformat() if r[1] else None)} for r in rows
    ])


def is_valid_ticker(symbol: str) -> bool:
    try:
        df = yf.Ticker(symbol).history(period="7d", interval="1d")
        app.logger.info("validate %s: history shape=%s", symbol, getattr(df, "shape", None))
        return not df.empty
    except Exception as e:
        app.logger.error("validate %s: EXC %r", symbol, e)
        return False

@app.post("/api/portfolio/<int:pid>/stocks")
def api_stock_add(pid: int):
    data = request.get_json(silent=True) or {}
    symbol = (data.get("symbol") or "").upper().strip()
    symbol = re.sub(r"[^A-Z0-9\.\-]", "", symbol)
    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    if not is_valid_ticker(symbol):
        return jsonify({"error": f"'{symbol}' is not a valid ticker."}), 400
    try:
        _exec("INSERT INTO portfolio_stocks (portfolio_id, stock_symbol) VALUES (%s,%s)",
              (pid, symbol))
        return jsonify({"ok": True, "symbol": symbol})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 409

@app.delete("/api/portfolio/<int:pid>/stocks")
def api_stock_delete(pid: int):
    data = request.get_json(silent=True) or {}
    symbol = (data.get("symbol") or "").upper().strip()
    symbol = re.sub(r"[^A-Z0-9\.\-]", "", symbol)
    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    _exec("DELETE FROM portfolio_stocks WHERE portfolio_id=%s AND stock_symbol=%s",
          (pid, symbol))
    return jsonify({"ok": True})
# For parquet
def load_prices_from_parquet(symbol: str, start: str, end: str) -> pd.DataFrame:
    file_path = os.path.join('data', f"{symbol}.parquet")
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    df = pd.read_parquet(file_path)

    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()
    
    df["dt"] = pd.to_datetime(df["dt"])
    
    mask = (df['dt'] >= pd.to_datetime(start)) & (df['dt'] <= pd.to_datetime(end))
    return df.loc[mask]

def get_portfolio_symbols(pid: int) -> list[str]:
    rows = _all("SELECT stock_symbol FROM portfolio_stocks WHERE portfolio_id=%s ORDER BY stock_symbol", (pid,))
    return [r[0] for r in rows]

#  Backtest Page 
@app.get("/backtest")
def backtest_page():
    pid = request.args.get("pid", type=int)
    return render_template("backtest.html", pid=pid)

#  /api/run endpoint
@app.post("/api/run")
def api_run():
    body = request.get_json(force=True) or {}
    pid = int(body.get("portfolio_id") or 0)
    start = body.get("start_date")
    end = body.get("end_date")
    cash_start = float(body.get("cash_start") or 0)
    params = body.get("params") or {}

    if not (pid and start and end and cash_start > 0):
        return jsonify({"error": "portfolio_id, start_date, end_date, cash_start required"}), 400

    symbols = get_portfolio_symbols(pid)
    if not symbols:
        return jsonify({"error": "No symbols in this portfolio."}), 400
        
    app.logger.info(f"Fetching data for {len(symbols)} symbols...")
    for sym in symbols:
        fetch_and_store_prices(sym, start, end)
    app.logger.info("Data fetching complete.")
    
    strategy_name = (params.get("strategy") or "sma").lower()
    res = {}
    
    if strategy_name == "sma":
        sma_params = {
            "short": int(params.get("short", 10)),
            "long":  int(params.get("long", 30)),
        }
        res = engine.run_backtest(
            symbols=symbols,
            start_date=start,
            end_date=end,
            cash_start=cash_start,
            price_loader=load_prices_from_parquet,
            strategy_logic=sma,
            strategy_params=sma_params
        )
    elif strategy_name == "consensus":
        res = engine.run_backtest(
            symbols=symbols,
            start_date=start,
            end_date=end,
            cash_start=cash_start,
            price_loader=load_prices_from_parquet,
            strategy_logic=consensus,
            strategy_params={} 
        )
    
    elif strategy_name == "ema_rsi":
        res = engine.run_backtest(
            symbols=symbols,
            start_date=start,
            end_date=end,
            cash_start=cash_start,
            price_loader=load_prices_from_parquet,
            strategy_logic=ema_rsi,
            strategy_params={} 
    )    

    app.logger.info("Backtest complete. Returning results to UI.")
    return jsonify(res)


# /api/save_session endpoint 
@app.post("/api/save_session")
def api_save_session():
    data = request.get_json(force=True)
    params = data.get("params", {})
    kpis = data.get("kpis", {})
    trades = data.get("trades", [])

    pid = params.get("portfolio_id")
    start = params.get("start_date")
    end = params.get("end_date")
    cash = params.get("cash_start")
    
    strategy_id = 1 

    try:
        session_id = _exec("""
            INSERT INTO sessions (portfolio_id, strategy_id, start_date, end_date, initial_cash, status)
            VALUES (%s, %s, %s, %s, %s, 'locked')
        """, (pid, strategy_id, start, end, cash))

        if trades:
            trade_inserts = []
            for trade in trades:
                trade_inserts.append((
                    session_id, trade['date'], trade['symbol'], trade['side'],
                    trade['price'], trade['qty']
                ))
            
            conn = get_connection()
            cur = conn.cursor()
            cur.executemany("""
                INSERT INTO session_trades (session_id, dt, stock_symbol, side, price, shares)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, trade_inserts)
            conn.commit()
            cur.close()
            conn.close()

        _exec("""
            INSERT INTO session_metrics (session_id, total_return, sharpe, max_drawdown, trades_count)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            session_id, kpis.get('total_pnl', 0), kpis.get('sharpe_ratio', 0),
            kpis.get('max_drawdown_pct', 0), len(trades)
        ))

        return jsonify({"ok": True, "session_id": session_id})
    except mysql.connector.Error as e:
        app.logger.error(f"Database save error: {e}")
        return jsonify({"error": str(e)}), 500



@app.post("/api/download_csv")
def api_download_csv():
    data = request.get_json(force=True)
    trades = data.get("trades", [])
    kpis = data.get("kpis", {})
    params = data.get("params", {})

    header = []
    header.append("# Backtest Report\n")
    header.append(f"# Strategy: {params.get('params', {}).get('strategy', 'N/A')}\n")
    header.append(f"# Date Range: {params.get('start_date', '')} to {params.get('end_date', '')}\n")
    header.append("-" * 30 + "\n")
    header.append("# Key Performance Indicators\n")
    header.append(f"# Final Portfolio Value: ${kpis.get('portfolio_value', 0):,.2f}\n")
    header.append(f"# Total P&L: ${kpis.get('total_pnl', 0):,.2f}\n")
    header.append(f"# Total Return: {kpis.get('return_pct', 0.0):.2f}%\n")
    header.append(f"# Sharpe Ratio: {kpis.get('sharpe_ratio', 0.0):.2f}\n")
    header.append(f"# Max Drawdown: {kpis.get('max_drawdown_pct', 0.0):.2f}%\n")
    header.append("-" * 30 + "\n")
    header.append("# Trades\n")
    
    summary_header = "".join(header)

    if not trades:
        csv_content = summary_header
    else:
        df = pd.DataFrame(trades)
        trades_csv = df.to_csv(index=False)
        csv_content = summary_header + trades_csv

    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

# ---------------------------- main ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)