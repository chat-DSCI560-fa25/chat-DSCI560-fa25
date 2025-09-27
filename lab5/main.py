# Lab5/main.py
import argparse
import time
from core import scraper, preprocessor, analysis, db_handler

def run_automation(interval_minutes):
    """
    Enhanced automation script that calls web scraping, pre-processing, 
    and storage periodically as required by the assignment.
    
    This script accepts interval parameter and provides proper status messages
    and error handling as specified in the requirements.
    """
    interval_seconds = interval_minutes * 60
    print(f"Starting automated data collection every {interval_minutes} minutes...")
    print("Press Ctrl+C to stop automation and enter interactive mode.")
    
    try:
        while True:
            print(f"\n{'='*60}")
            print(f"AUTOMATED RUN - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # Step 1: Fetch new data
                print("Fetching new data from Reddit...")
                scraper.fetch_posts("programming", 100)
                print("Data fetching completed successfully.")
                
                # Step 2: Preprocess data
                print("\nProcessing and cleaning data...")
                preprocessor.run_preprocessor()
                print("Data preprocessing completed successfully.")
                
                # Step 3: Update analysis (optional, can be resource intensive)
                print("\nUpdating clustering analysis...")
                analysis.run_analysis()
                print("Analysis update completed successfully.")
                
                print(f"\nDatabase update completed successfully!")
                
            except Exception as e:
                print(f"Error during automated run: {e}")
                print("Continuing with next scheduled run...")
            
            print(f"\nNext run in {interval_minutes} minutes...")
            print(f"Sleeping until {time.strftime('%H:%M:%S', time.localtime(time.time() + interval_seconds))}")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\nAutomation stopped by user.")
        print("Switching to interactive mode...")
        run_interactive()

def run_interactive():
    """
    Enhanced interactive mode that takes keywords or messages as input
    and finds the closest matching cluster as required by the assignment.
    
    Displays messages from selected cluster with graphical representation
    when possible.
    """
    print("\n" + "="*60)
    print("INTERACTIVE CLUSTER SEARCH MODE")
    print("="*60)
    print("Enter keywords or a message to find the best matching cluster.")
    print("The system will display similar posts from the matched cluster.")
    print("Commands:")
    print("  - Type any text to search for matching clusters")
    print("  - Type 'help' for usage examples")
    print("  - Type 'stats' to see cluster statistics")
    print("  - Type 'quit' or 'exit' to stop")
    print("-" * 60)
    
    connection = db_handler.create_connection()
    if not connection:
        print("Could not connect to database.")
        return

    while True:
        try:
            query = input("\nSearch> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            elif query.lower() == 'help':
                print("\nUsage Examples:")
                print("  - 'python programming'     - Find posts about Python")
                print("  - 'machine learning AI'    - Find ML/AI related posts")
                print("  - 'web development'        - Find web dev posts")
                print("  - 'database SQL'           - Find database posts")
                print("  - 'javascript react'       - Find JS/React posts")
                continue
            elif query.lower() == 'stats':
                display_cluster_stats(connection)
                continue
            elif not query:
                print("Please enter a search query or 'help' for examples.")
                continue
            
            # Find matching cluster
            cluster_id = analysis.find_matching_cluster(query)
            
            if cluster_id is not None:
                print(f"\nBest match: Cluster {cluster_id}")
                
                # Get posts from the cluster
                posts = db_handler.fetch_posts_by_cluster(connection, cluster_id)
                
                if posts:
                    print(f"Found {len(posts)} posts in this cluster:")
                    print("-" * 50)
                    
                    # Display top posts with better formatting
                    for i, post in enumerate(posts[:8], 1):  # Show top 8 posts
                        title = post['title']
                        if len(title) > 70:
                            title = title[:67] + "..."
                        print(f"  {i:2d}. {title}")
                    
                    if len(posts) > 8:
                        print(f"     ... and {len(posts) - 8} more posts")
                    
                    # Try to create a simple visualization
                    try:
                        create_cluster_visualization(connection, cluster_id)
                    except Exception as e:
                        print(f"Note: Could not create visualization: {e}")
                        
                else:
                    print("Could not find any posts for this cluster.")
            else:
                print("Could not determine matching cluster. Try a different query.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error during search: {e}")
            
    print("\nExiting interactive mode.")
    connection.close()

def display_cluster_stats(connection):
    """Display statistics about all clusters."""
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT cluster_id, COUNT(*) as post_count 
        FROM reddit_posts 
        WHERE cluster_id IS NOT NULL 
        GROUP BY cluster_id 
        ORDER BY cluster_id
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        if results:
            print("\nCluster Statistics:")
            print("-" * 30)
            total_posts = sum(r['post_count'] for r in results)
            for result in results:
                cluster_id = result['cluster_id']
                count = result['post_count']
                percentage = (count / total_posts) * 100
                print(f"  Cluster {cluster_id}: {count:3d} posts ({percentage:5.1f}%)")
            print(f"  Total:     {total_posts:3d} posts")
        else:
            print("No cluster data found. Please run analysis first.")
            
    except Exception as e:
        print(f"Error getting cluster stats: {e}")

def create_cluster_visualization(connection, cluster_id):
    """Create a simple text-based visualization for the cluster."""
    try:
        # Get sample posts from cluster for keyword analysis
        cursor = connection.cursor(dictionary=True)
        query = "SELECT title, post_body_cleaned FROM reddit_posts WHERE cluster_id = %s LIMIT 20"
        cursor.execute(query, (cluster_id,))
        posts = cursor.fetchall()
        cursor.close()
        
        if posts:
            # Simple keyword frequency analysis
            from collections import Counter
            all_text = ' '.join([
                (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).lower()
                for post in posts
            ])
            
            words = all_text.split()
            # Filter common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                           'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have'}
            
            word_freq = Counter([w for w in words if len(w) > 2 and w not in common_words and w.isalpha()])
            
            if word_freq:
                print(f"\nTop keywords in Cluster {cluster_id}:")
                for word, freq in word_freq.most_common(8):
                    bar_length = min(20, freq)
                    bar = "#" * bar_length
                    print(f"  {word:12s} {bar} ({freq})")
                    
    except Exception as e:
        pass  # Silently fail if visualization can't be created

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reddit Data Collection, Processing, and Clustering System - DSCI 560 Lab 5",
        epilog="""
Examples:
  python main.py                    # Interactive mode
  python main.py 5                  # Automation mode (every 5 minutes)
  python main.py --scrape           # Scrape new posts once
  python main.py --analyze          # Run full analysis pipeline
  python main.py --interpret        # View clustering results with visualization
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional argument for automation interval (as required by assignment)
    parser.add_argument("interval", nargs='?', type=int, 
                       help="Run in automation mode at this interval in minutes (e.g., 'python main.py 5')")
    
    # Optional arguments for individual operations
    parser.add_argument("--scrape", action="store_true", 
                       help="Run the Reddit scraper once to fetch new posts")
    parser.add_argument("--preprocess", action="store_true", 
                       help="Run data preprocessing on unprocessed posts")
    parser.add_argument("--analyze", action="store_true", 
                       help="Run complete analysis pipeline (embedding + clustering)")
    parser.add_argument("--interpret", action="store_true", 
                       help="Interpret and visualize clustering results")
    parser.add_argument("--posts", type=int, default=100,
                       help="Number of posts to scrape (default: 100, max: 1000)")
    parser.add_argument("--subreddit", type=str, default="programming",
                       help="Subreddit to scrape from (default: programming)")
    
    args = parser.parse_args()

    # Handle command line arguments as specified in assignment
    if args.interval:
        # Automation mode: "python filename.py 5" runs every 5 minutes
        run_automation(args.interval)
    elif args.scrape:
        print(f"Scraping {args.posts} posts from r/{args.subreddit}...")
        scraper.fetch_posts(args.subreddit, min(args.posts, 1000))  # Respect API limits
    elif args.preprocess:
        print("Running data preprocessing...")
        preprocessor.run_preprocessor()
    elif args.analyze:
        print("Running complete analysis pipeline...")
        analysis.run_analysis()
    elif args.interpret:
        print("Interpreting clustering results...")
        analysis.interpret_clusters()
    else:
        # Default: Interactive mode for keyword/message input
        run_interactive()