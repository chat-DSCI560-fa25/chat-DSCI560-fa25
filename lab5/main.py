# Lab5/main.py
import argparse
import time
from core import scraper, preprocessor, analysis, db_handler

def run_automation(interval_minutes):
    """Runs the scraper and preprocessor in a loop."""
    interval_seconds = interval_minutes * 60
    while True:
        print(f"\n--- Starting scheduled run ---")
        print("Fetching new data...")
        scraper.fetch_posts("programming", 100) # Fetches 100 new posts
        
        print("\nProcessing data...")
        preprocessor.run_preprocessor()
        
        print(f"\n--- Run complete. Sleeping for {interval_minutes} minutes. ---")
        time.sleep(interval_seconds)

def run_interactive():
    """I am experimenting with this,an interactive prompt to find matching clusters."""
    print("\n--- Starting Interactive Mode ---")
    print("Enter a keyword or sentence to find the best matching cluster.")
    print("Type 'quit' or 'exit' to stop.")
    
    connection = db_handler.create_connection()
    if not connection:
        return

    while True:
        try:
            query = input("> ")
            if query.lower() in ['quit', 'exit']:
                break
            
            cluster_id = analysis.find_matching_cluster(query)
            
            if cluster_id is not None:
                print(f"Your query matches best with Cluster {cluster_id}.")
                posts = db_handler.fetch_posts_by_cluster(connection, cluster_id)
                if posts:
                    print("Here are some posts from that cluster:")
                    for post in posts:
                        print(f"  - {post['title']}")
                else:
                    print("Could not find any posts for this cluster.")
        except KeyboardInterrupt:
            break
            
    print("\nExiting interactive mode.")
    connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape, process, and analyze Reddit data.")
    
    parser.add_argument("--interval", type=int, help="Run in automation mode at this interval in minutes.")
    parser.add_argument("--scrape", action="store_true", help="Run the scraper once.")
    parser.add_argument("--preprocess", action="store_true", help="Run the data preprocessor once.")
    parser.add_argument("--analyze", action="store_true", help="Run the analysis and clustering model once.")
    parser.add_argument("--interpret", action="store_true", help="Interpret and display the clustering results.")
    
    args = parser.parse_args()

    if args.interval:
        run_automation(args.interval)
    elif args.scrape:
        scraper.fetch_posts("programming", 100)
    elif args.preprocess:
        preprocessor.run_preprocessor()
    elif args.analyze:
        analysis.run_analysis()
    elif args.interpret:
        analysis.interpret_clusters()
    else:
        run_interactive()