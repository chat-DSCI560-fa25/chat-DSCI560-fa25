import mysql.connector
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

def get_conn(database=None):
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database or MYSQL_DB
    )

def init_db():
    root_conn = mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD
    )
    root_cur = root_conn.cursor()
    root_cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} DEFAULT CHARACTER SET 'utf8mb4'")
    root_cur.close()
    root_conn.close()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reddit_posts (
        id VARCHAR(20) PRIMARY KEY,
        subreddit VARCHAR(128),
        title TEXT,
        content_clean MEDIUMTEXT,
        author_masked VARCHAR(64),
        created_utc_iso VARCHAR(32),
        score INT,
        num_comments INT,
        url TEXT,
        keywords JSON,
        ocr_text MEDIUMTEXT
    ) CHARACTER SET utf8mb4
    """)
    conn.commit()
    cur.close()
    conn.close()
