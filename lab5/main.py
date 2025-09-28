# main.py

import argparse
import time
from core import scraper, preprocessor, analysis

def run_automation(interval_minutes):
    """Runs the full data pipeline in a loop."""
    while True:
        print(f"--- [Worker] Starting scheduled run ---")
        try:
            print("--- [Worker] Scraping new data... ---")
            # For automation, we always get the latest 'new' posts
            scraper.fetch_posts("programming", 100) 
            
            print("--- [Worker] Preprocessing new data... ---")
            preprocessor.run_preprocessor()

            print("--- [Worker] Analyzing new data... ---")
            analysis.run_analysis()
            
            print(f"--- [Worker] Run complete. Sleeping for {interval_minutes} minutes. ---")
            time.sleep(interval_minutes * 60)
            
        except Exception as e:
            print(f"--- [Worker] An error occurred: {e} ---")
            print(f"--- [Worker] Retrying in 5 minutes. ---")
            time.sleep(300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reddit Data Scraper and Analyzer")
    
    # Mode Flags
    parser.add_argument("--interval", type=int, help="Run in continuous automation mode at this interval in minutes.")
    parser.add_argument("--scrape", action="store_true", help="Run the scraper once.")
    parser.add_argument("--preprocess", action="store_true", help="Run the data preprocessor once.")
    parser.add_argument("--analyze", action="store_true", help="Run the analysis and clustering model once.")
    parser.add_argument("--interpret", action="store_true", help="Interpret and display the clustering results.")
    
    # Options for Manual Scraping
    parser.add_argument("--limit", type=int, default=100, help="Number of posts to fetch for a manual scrape.")
    parser.add_argument("--subreddit", type=str, default="programming", help="Subreddit for a manual scrape.")
    
    args = parser.parse_args()

    # Logic to decide which action to take
    if args.interval:
        run_automation(args.interval)
    elif args.scrape:
        scraper.fetch_posts(args.subreddit, args.limit)
    elif args.preprocess:
        preprocessor.run_preprocessor()
    elif args.analyze:
        analysis.run_analysis()
    elif args.interpret:
        analysis.interpret_clusters()
    else:
        parser.print_help()