# sotcks.py
from db_config import get_connection
from portfolio import list_portfolios   # reuse instead of redefining

def input_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            return int(s)
        print("Please enter a valid int vlaue.")

def show_portfolio_stocks():
    rows = list_portfolios()
    if not rows:
        return
    pid = input_int("Enter portfolio ID to view stocks: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_symbol, added_at
          FROM portfolio_stocks
         WHERE portfolio_id = %s
         ORDER BY added_at DESC;
    """, (pid,))
    stocks = cur.fetchall()
    cur.close()
    conn.close()

    if not stocks:
        print("(No stocks in this portfolio)")
        return

    print(f"\nStocks in portfolio {pid}:")
    for sym, added in stocks:
        print(f"- {sym} (added {added})")
    print()

def add_stock_to_portfolio():
    rows = list_portfolios()
    if not rows:
        return
    pid = input_int("Enter portfolio ID to add a stock to: ")
    symbol = input("Enter stock symbol example: AAPL): ").upper().strip()
    if not symbol:
        print("Symbol needed")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO portfolio_stocks (portfolio_id, stock_symbol) VALUES (%s, %s);",
            (pid, symbol),
        )
        conn.commit()
        print("Stock added.Success!!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def remove_stock_from_portfolio():
    rows = list_portfolios()
    if not rows:
        return
    pid = input_int("Enter portfolio ID to remove a stock from: ")
    symbol = input("Enter stock symbol to remove example AAPL: ").upper().strip()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM portfolio_stocks WHERE portfolio_id=%s AND stock_symbol=%s;",
        (pid, symbol),
    )
    conn.commit()
    if cur.rowcount > 0:
        print("Stock removed.")
    else:
        print("Nothing removed.")
    cur.close()
    conn.close()

def menu():
    while True:
        print("""
**********************
 Stocks Manager
**********************
1) Show stocks in a portfolio
2) Add stock to a portfolio
3) Remove stock from a portfolio
0) Exit
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_portfolio_stocks()
        elif choice == "2":
            add_stock_to_portfolio()
        elif choice == "3":
            remove_stock_from_portfolio()
        elif choice == "0":
            print("Back to main menu.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    menu()
