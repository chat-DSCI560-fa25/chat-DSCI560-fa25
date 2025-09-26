from scraper import fetch_posts
from preprocess import clean_text, mask_username, extract_keywords, extract_ocr
from storage import insert_many
from db import init_db
from datetime import datetime

def run_pipeline(subreddit, limit):
    init_db()
    raw_posts = fetch_posts(subreddit, limit)

    processed = []
    for s in raw_posts:
        text = clean_text(s.selftext or "")
        keywords = extract_keywords(text)
        processed.append({
            "id": s.id,
            "subreddit": subreddit,
            "title": s.title,
            "content_clean": text,
            "author_masked": mask_username(str(s.author)),
            "created_utc_iso": datetime.utcfromtimestamp(s.created_utc).isoformat(),
            "score": s.score,
            "num_comments": s.num_comments,
            "url": s.url,
            "keywords": keywords,
            "ocr_text": ""  # placeholder for OCR
        })

    insert_many(processed)
    return processed
