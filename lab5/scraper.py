import praw, time
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

def fetch_posts(subreddit_name, limit=5000, batch_size=1000, sleep_sec=2, max_runtime=400):
    """
    Fetch posts from a subreddit in batches, respecting Reddit API limits.
    
    Args:
        subreddit_name (str): Subreddit to scrape.
        limit (int): Total number of posts to fetch (max ~5000).
        batch_size (int): Number of posts per batch (<=1000).
        sleep_sec (int): Pause between batches to avoid rate limits.
        max_runtime (int): Max seconds allowed for scraping.
    
    Returns:
        list of praw.models.Submission
    """
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        check_for_async=False 
    )
    subreddit = reddit.subreddit(subreddit_name)

    posts = []
    start_time = time.time()

    # PRAW's .new() or .hot() can yield >1000 if you don't set limit, but we enforce batching
    fetched = 0
    after = None

    while fetched < limit and (time.time() - start_time) < max_runtime:
        remaining = limit - fetched
        this_batch = min(batch_size, remaining)

        # Fetch a batch
        batch_posts = list(subreddit.new(limit=this_batch, params={"after": after}))
        if not batch_posts:
            break  # no more posts available

        posts.extend(batch_posts)
        fetched += len(batch_posts)
        after = batch_posts[-1].fullname  # pagination anchor

        print(f"[Scraper] Fetched {fetched}/{limit} posts so far...")

        # Respect API rate limits
        time.sleep(sleep_sec)

    print(f"[Scraper] Done. Collected {len(posts)} posts in {int(time.time()-start_time)}s")
    return posts
