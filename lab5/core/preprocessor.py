import re
from core import db_handler

def clean_text(text):
    """Cleans a single string of text."""
    if not text:
        return ""
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove special characters and numbers, keep only letters and basic punctuation
    text = re.sub(r'[^a-zA-Z\s\.]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def run_preprocessor():
    
    print("Starting preprocessing...")
    connection = db_handler.create_connection()
    if not connection:
        return

    posts_to_process = db_handler.fetch_unprocessed_posts(connection)
    if not posts_to_process:
        print("No new posts to process.")
        connection.close()
        return

    print(f"Found {len(posts_to_process)} posts to clean.")
    
    for post in posts_to_process:
        combined_text = post['title'] + " " + post['post_body_raw']
        cleaned_body = clean_text(post['post_body_raw'])
        db_handler.update_cleaned_post(connection, post['id'], cleaned_body)
        print(f"Cleaned and updated post: {post['id']}")

    print("Preprocessing finished.")
    connection.close()