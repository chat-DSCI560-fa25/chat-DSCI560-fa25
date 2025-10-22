import praw
import config
from core import db_handler
import hashlib

def get_reddit_instance():
    
    return praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )

def mask_username(username):
    if username is None:
        return "deleted_user"
    return hashlib.sha256(username.encode()).hexdigest()

def fetch_posts(subreddit_name, post_limit):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)
    
    print(f"Connecting to database to store {post_limit} posts from r/{subreddit_name}...")
    connection = db_handler.create_connection()
    if not connection:
        return 

    db_handler.create_table(connection)

    print("Starting to fetch posts...")
    fetched_count = 0
    for post in subreddit.new(limit=300):
        author_name = post.author.name if post.author else None
        
        post_data = (
            post.id,
            subreddit.display_name,
            post.title,
            mask_username(author_name),
            post.created_utc,
            post.selftext
        )
        
        db_handler.insert_post(connection, post_data)
        fetched_count += 1
        print(f"Fetched and stored post {fetched_count}/{post_limit}: {post.id}")
        
    print(f"\nFinished fetching {fetched_count} posts.")
    connection.close()
    print("Database connection closed.")