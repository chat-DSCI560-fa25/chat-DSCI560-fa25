# Managing the portfolio
from db_config import get_connection

def create_portfolio():
    name = input("Enter a new portfolio name: ").strip()
    if not name:
        print("Portfolio name is needed!!!")
        return
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO portfolios (portfolio_name) VALUES (%s);", (name,))
        conn.commit()
        print("Your portfolio is created.Woah!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def list_portfolios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT portfolio_id, portfolio_name, created_at FROM portfolios;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("(There are no portfolios yet!)")
        return
    print("\nPortfolios:")
    for pid, name, created in rows:
        print(f"- ID={pid} | Name={name} | Created={created}")
    print()
    return rows

def menu():
    while True:
        print("""
**********************
 Portfolio Manager
**********************
1) Create a brand new portfolio
2) List existing portfolios
0) Exit
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            create_portfolio()
        elif choice == "2":
            list_portfolios()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    menu()
