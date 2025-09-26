import json
from db import get_conn

def insert_many(posts):
    if not posts: return
    conn = get_conn()
    cur = conn.cursor()

    sql = """
    INSERT INTO reddit_posts (
        id, subreddit, title, content_clean, author_masked, created_utc_iso,
        score, num_comments, url, keywords, ocr_text
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        subreddit=VALUES(subreddit),
        title=VALUES(title),
        content_clean=VALUES(content_clean),
        author_masked=VALUES(author_masked),
        created_utc_iso=VALUES(created_utc_iso),
        score=VALUES(score),
        num_comments=VALUES(num_comments),
        url=VALUES(url),
        keywords=VALUES(keywords),
        ocr_text=VALUES(ocr_text)
    """

    payload = []
    for p in posts:
        payload.append((
            p["id"], p["subreddit"], p["title"], p["content_clean"],
            p["author_masked"], p["created_utc_iso"], p["score"],
            p["num_comments"], p["url"], json.dumps(p["keywords"]),
            p["ocr_text"]
        ))

    cur.executemany(sql, payload)
    conn.commit()
    cur.close()
    conn.close()
