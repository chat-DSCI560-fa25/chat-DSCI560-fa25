import mysql.connector
import pandas as pd
from pipeline import run_pipeline
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

def main():
    # Run the pipeline (scrape + preprocess + store)
    posts = run_pipeline("cybersecurity", 2000)
    print(f"Stored {len(posts)} posts")

    # Fetch data back into Pandas for analysis
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    df = pd.read_sql("SELECT id, content_clean FROM reddit_posts", conn)
    conn.close()

    print("Sample rows from DB:")
    print(df.head())

if __name__ == "__main__":
    main()
