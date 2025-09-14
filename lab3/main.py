# The mainn Menuuu
#Below we import the files to perform various operations
from prices import fetch_and_store_for_portfolio, query_prices
import portfolio  # provides portfolio.menu()
import stocks     # provides stocks.menu()

def input_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            return int(s)
        print("Please enter a valid integer.")

def main_menu():
    while True:
        print("""
####################################
 Stock Portfolio Manager—  Main Menu
####################################
1) Portfolio manager
2) Stocks manager
3) Fetch & store prices using portfolio
4) Query stored prices by symbol
0) Exit
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            portfolio.menu()  
        elif choice == "2":
            stocks.menu()     
        elif choice == "3":
            pid = input_int("Portfolio ID: ")
            start = input("Start date (YYYY-MM-DD): ").strip()
            end   = input("End date   (YYYY-MM-DD): ").strip()
            inserted, updated = fetch_and_store_for_portfolio(pid, start, end)
            print(f"Done. Inserted={inserted}, Updated={updated}")
        elif choice == "4":
            symbol = input("Symbol (e.g., AAPL): ").upper().strip()
            start  = input("Start date (YYYY-MM-DD): ").strip()
            end    = input("End date   (YYYY-MM-DD): ").strip()
            rows = query_prices(symbol, start, end)
            if not rows:
                print("No rows found.")
            else:
                print(f"\n{symbol} prices:")
                print("dt         open      high       low     close     volume")
                for dt, o, h, l, c, v in rows:
                    v_str = str(v) if v is not None else ""
                    print(f"{dt}  {o:9.4f} {h:9.4f} {l:9.4f} {c:9.4f} {v_str}")
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main_menu()
