import argparse
from core import scraper, preprocessor, analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape, process, and analyze Reddit data.")
    
    # --- Action Flags ---
    parser.add_argument("--scrape", action="store_true", help="Run the scraper once.")
    parser.add_argument("--preprocess", action="store_true", help="Run the data preprocessor once.")
    parser.add_argument("--analyze", action="store_true", help="Run the analysis and clustering model once.")
    parser.add_argument("--interpret", action="store_true", help="Interpret and display the clustering results.")
    
    # --- Options for Scraping ---
    parser.add_argument("--limit", type=int, default=100, help="Number of posts to fetch during a scrape.")
    parser.add_argument("--subreddit", type=str, default="programming", help="Name of the subreddit to scrape.")
    
    args = parser.parse_args()

    # The script now runs only one action per command
    if args.scrape:
        # Use the limit and subreddit from the command line
        scraper.fetch_posts(args.subreddit, args.limit)
    elif args.preprocess:
        preprocessor.run_preprocessor()
    elif args.analyze:
        analysis.run_analysis()
    elif args.interpret:
        analysis.interpret_clusters()
    else:
        # If no action is specified, print the help message
        parser.print_help()