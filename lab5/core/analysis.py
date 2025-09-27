import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from core import db_handler
from scipy.spatial import distance
import pickle 
import os


"""
Enhanced analysis module that implements clustering algorithms as required by the assignment.
This module converts messages into vector embeddings and performs clustering analysis
with visualization capabilities.
"""
def create_document_embeddings(posts):
    """
    Create document embeddings using Doc2Vec as required by the assignment.
    This implements content abstraction for clustering analysis.
    """
    print("Creating document embeddings using Doc2Vec...")
    
    # Prepare documents for Doc2Vec
    documents = []
    for i, post in enumerate(posts):
        # Combine title and body for richer content representation
        text = (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        if text:
            # Tokenize and create TaggedDocument
            words = text.lower().split()
            documents.append(TaggedDocument(words, [i]))
    
    if not documents:
        print("No valid documents found for embedding.")
        return None
    
    # Train Doc2Vec model with improved parameters for better differentiation
    model = Doc2Vec(
        documents,
        vector_size=150,        # Increased dimension for better feature representation
        window=8,               # Larger context window
        min_count=1,            # Include more words (important for small dataset)
        workers=4,              # Number of worker threads
        epochs=100,             # More training iterations for better convergence
        dm=0,                   # Use distributed bag of words (PV-DBOW) for better clustering
        alpha=0.05,             # Higher initial learning rate
        min_alpha=0.001,        # Higher minimum learning rate
        negative=10,            # Negative sampling for better word representations
        hs=0                    # Use negative sampling instead of hierarchical softmax
    )
    
    # Additional training with shuffled data for better convergence
    for epoch in range(20):
        model.train(documents, total_examples=len(documents), epochs=1)
        model.alpha -= 0.002  # Decrease learning rate
        model.min_alpha = model.alpha
    
    # Save the trained model
    os.makedirs("models", exist_ok=True)
    model.save("models/doc2vec.model")
    print("Doc2Vec model trained and saved.")
    
    return model

def find_optimal_clusters(vectors, max_k=10):
    """
    Find optimal number of clusters using silhouette analysis
    as required for clustering algorithm implementation.
    """
    if len(vectors) < 4:
        return 2
        
    silhouette_scores = []
    k_range = range(2, min(max_k + 1, len(vectors)))
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(vectors)
        
        try:
            silhouette_avg = silhouette_score(vectors, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        except:
            silhouette_scores.append(0)
    
    if silhouette_scores:
        optimal_k = k_range[silhouette_scores.index(max(silhouette_scores))]
        print(f"Optimal number of clusters: {optimal_k} (silhouette score: {max(silhouette_scores):.3f})")
        return optimal_k
    
    return 5  # Default fallback

def extract_cluster_keywords(posts, cluster_labels, n_keywords=10):
    """
    Extract keywords associated with messages in each cluster
    as required by the assignment.
    """
    cluster_keywords = {}
    
    # Group posts by cluster
    clusters = {}
    for i, post in enumerate(posts):
        cluster_id = cluster_labels[i]
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        
        # Combine title and text for keyword extraction
        text = (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        if text:
            clusters[cluster_id].append(text)
    
    # Extract keywords for each cluster
    for cluster_id, texts in clusters.items():
        # Combine all texts in cluster
        combined_text = ' '.join(texts).lower()
        
        # Simple keyword extraction (you can enhance this with TF-IDF)
        words = combined_text.split()
        word_freq = Counter(words)
        
        # Filter out common words and get top keywords
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                       'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                       'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                       'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        keywords = []
        for word, freq in word_freq.most_common():
            if (len(word) > 2 and 
                word not in common_words and 
                word.isalpha() and
                len(keywords) < n_keywords):
                keywords.append((word, freq))
        
        cluster_keywords[cluster_id] = keywords
    
    return cluster_keywords

def run_analysis():
    """
    Enhanced analysis function that implements clustering algorithms
    as required by the assignment with comprehensive analysis.
    """
    print("Starting comprehensive analysis...")
    connection = db_handler.create_connection()
    if not connection:
        return

    posts = db_handler.fetch_cleaned_posts(connection)
    if not posts or len(posts) < 5:
        print("Not enough posts to analyze (minimum 5 required).")
        connection.close()
        return

    print(f"Found {len(posts)} posts to analyze.")
    
    # Step 1: Create document embeddings (message content abstraction)
    model = create_document_embeddings(posts)
    
    # Step 2: Generate vectors for all posts
    vectors = []
    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        if text:
            vector = model.infer_vector(text.split())
            vectors.append(vector.astype(np.float64))  # Ensure consistent data type
        else:
            vectors.append(np.zeros(model.vector_size, dtype=np.float64))
    
    vectors = np.array(vectors, dtype=np.float64)
    
    # Step 3: Find optimal number of clusters
    optimal_k = find_optimal_clusters(vectors)
    
    # Step 4: Perform K-means clustering with improved parameters
    print(f"Performing K-means clustering with {optimal_k} clusters...")
    kmeans = KMeans(
        n_clusters=optimal_k, 
        random_state=42, 
        n_init=20,              # More initializations to find better centroids
        max_iter=500,           # More iterations for convergence
        algorithm='lloyd',      # Use Lloyd's algorithm for better results
        init='k-means++'        # Smart initialization
    )
    cluster_labels = kmeans.fit_predict(vectors)
    
    # Save the clustering model
    with open("models/kmeans.pkl", "wb") as f:
        pickle.dump(kmeans, f)
    print("K-Means clustering model saved.")
    
    # Step 5: Extract keywords for each cluster
    cluster_keywords = extract_cluster_keywords(posts, cluster_labels)
    
    # Step 6: Update database with analysis results
    for i, post in enumerate(posts):
        post_id = post['id']
        vector = vectors[i]
        cluster_id = int(cluster_labels[i])
        
        db_handler.update_post_analysis(connection, post_id, vector, cluster_id)
        print(f"Updated post {post_id} with vector and cluster ID {cluster_id}")
    
    # Step 7: Display clustering results
    print(f"\n=== CLUSTERING RESULTS ===")
    print(f"Total posts analyzed: {len(posts)}")
    print(f"Number of clusters: {optimal_k}")
    
    for cluster_id in range(optimal_k):
        cluster_posts = [posts[i] for i in range(len(posts)) if cluster_labels[i] == cluster_id]
        keywords = cluster_keywords.get(cluster_id, [])
        
        print(f"\nCluster {cluster_id}: {len(cluster_posts)} posts")
        if keywords:
            keyword_str = ', '.join([word for word, _ in keywords[:5]])
            print(f"  Top keywords: {keyword_str}")
        
        # Show sample post titles
        sample_titles = [post.get('title', 'No title')[:60] + '...' 
                        for post in cluster_posts[:3]]
        for title in sample_titles:
            print(f"  - {title}")

    print("\nAnalysis finished successfully.")
    connection.close()


def create_visualization(save_path="visualizations"):
    """
    Create visualization of clustering results as required by the assignment.
    Uses matplotlib to display K clusters of messages and their keywords.
    """
    print("Creating cluster visualizations...")
    
    try:
        # Load models
        with open("models/kmeans.pkl", "rb") as f:
            kmeans = pickle.load(f)
        
        connection = db_handler.create_connection()
        if not connection:
            return
            
        posts = db_handler.fetch_all_analyzed_posts(connection)
        if not posts:
            print("No analyzed posts found.")
            connection.close()
            return
        
        # Create visualizations directory
        os.makedirs(save_path, exist_ok=True)
        
        # Group posts by cluster for analysis
        clusters = {}
        for post in posts:
            cluster_id = post['cluster_id']
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(post)
        
        # Create cluster size visualization
        cluster_sizes = [len(clusters.get(i, [])) for i in range(len(kmeans.cluster_centers_))]
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(cluster_sizes)), cluster_sizes, color='skyblue', edgecolor='navy', alpha=0.7)
        plt.xlabel('Cluster ID')
        plt.ylabel('Number of Posts')
        plt.title('Distribution of Posts Across Clusters')
        plt.xticks(range(len(cluster_sizes)))
        
        # Add value labels on bars
        for i, v in enumerate(cluster_sizes):
            plt.text(i, v + 0.5, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f"{save_path}/cluster_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create word clouds for each cluster
        for cluster_id, cluster_posts in clusters.items():
            if cluster_posts:
                # Combine all text in cluster
                cluster_text = ' '.join([
                    (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
                    for post in cluster_posts
                ])
                
                if cluster_text and len(cluster_text) > 50:
                    try:
                        wordcloud = WordCloud(
                            width=800, height=400, 
                            background_color='white',
                            max_words=50,
                            colormap='viridis'
                        ).generate(cluster_text)
                        
                        plt.figure(figsize=(10, 5))
                        plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis('off')
                        plt.title(f'Cluster {cluster_id} Word Cloud ({len(cluster_posts)} posts)')
                        plt.tight_layout()
                        plt.savefig(f"{save_path}/cluster_{cluster_id}_wordcloud.png", 
                                  dpi=300, bbox_inches='tight')
                        plt.close()
                    except Exception as e:
                        print(f"Could not create word cloud for cluster {cluster_id}: {e}")
        
        print(f"Visualizations saved to {save_path}/ directory")
        connection.close()
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")

def interpret_clusters():
    """
    Enhanced cluster interpretation with detailed analysis and visualization
    as required by the assignment to verify cluster content similarity.
    """
    print("Interpreting clusters with detailed analysis...")
    try:
        with open("models/kmeans.pkl", "rb") as f:
            kmeans = pickle.load(f)
        print("KMeans model loaded successfully.")

    except FileNotFoundError:
        print("Model files not found. Please run the analysis first with --analyze.")
        return

    connection = db_handler.create_connection()
    if not connection: 
        return

    posts = db_handler.fetch_all_analyzed_posts(connection)
    if not posts:
        print("No analyzed posts found in the database.")
        connection.close()
        return
    
    # Group posts by cluster
    clusters = {}
    for post in posts:
        cluster_id = post['cluster_id']
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(post)
    
    centroids = kmeans.cluster_centers_
    
    print(f"\n{'='*60}")
    print(f"CLUSTER INTERPRETATION RESULTS")
    print(f"{'='*60}")
    print(f"Total clusters: {len(centroids)}")
    print(f"Total posts analyzed: {len(posts)}")
    
    for cluster_id, centroid in enumerate(centroids):
        cluster_posts = clusters.get(cluster_id, [])
        
        print(f"\n{'-'*50}")
        print(f"CLUSTER {cluster_id}")
        print(f"{'-'*50}")
        print(f"Number of posts: {len(cluster_posts)}")
        
        if not cluster_posts:
            print("No posts in this cluster.")
            continue
        
        # Find most representative posts (closest to centroid)
        try:
            post_vectors = np.array([np.frombuffer(post['embedding_vector'], dtype=np.float64) 
                                   for post in cluster_posts])
            distances = distance.cdist(post_vectors, [centroid], 'euclidean').flatten()
            closest_indices = distances.argsort()[:5]
            
            print("Most representative posts (closest to centroid):")
            for i, index in enumerate(closest_indices, 1):
                title = cluster_posts[index]['title'][:80] + '...' if len(cluster_posts[index]['title']) > 80 else cluster_posts[index]['title']
                print(f"  {i}. {title}")
                
        except Exception as e:
            print(f"Could not calculate distances: {e}")
            print("Sample posts from this cluster:")
            for i, post in enumerate(cluster_posts[:5], 1):
                title = post['title'][:80] + '...' if len(post['title']) > 80 else post['title']
                print(f"  {i}. {title}")
        
        # Extract and display cluster keywords
        cluster_text = ' '.join([
            (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
            for post in cluster_posts
        ])
        
        if cluster_text:
            words = cluster_text.lower().split()
            word_freq = Counter(words)
            
            # Filter common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                           'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                           'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            
            keywords = []
            for word, freq in word_freq.most_common(20):
                if len(word) > 2 and word not in common_words and word.isalpha():
                    keywords.append(f"{word}({freq})")
                    if len(keywords) >= 10:
                        break
            
            if keywords:
                print(f"Top keywords: {', '.join(keywords)}")
    
    print(f"\n{'='*60}")
    
    # Create visualizations
    create_visualization()
    
    connection.close()    

def find_matching_cluster(query_text):
    """
    Find the best matching cluster for a query text using hybrid approach.
    Uses both semantic similarity and keyword matching for better accuracy.
    """
    try:
        # Load trained models
        model = Doc2Vec.load("models/doc2vec.model")
        with open("models/kmeans.pkl", "rb") as f:
            kmeans = pickle.load(f)
        
        # Try to load TF-IDF vectorizer if available
        try:
            with open("models/tfidf.pkl", "rb") as f:
                tfidf = pickle.load(f)
            use_tfidf = True
        except:
            use_tfidf = False
            
    except FileNotFoundError:
        print("Model files not found. Please run --analyze first.")
        return None

    # Clean and process query text
    from .preprocessor import clean_text
    cleaned_query = clean_text(query_text)
    
    if not cleaned_query.strip():
        return None
    
    # Method 1: Doc2Vec approach
    vector = model.infer_vector(cleaned_query.split())
    vector = vector.astype(np.float64)
    doc2vec_cluster = kmeans.predict([vector])[0]
    
    # Method 2: If we have diverse clusters, use keyword-based matching
    connection = db_handler.create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get cluster statistics
        cursor.execute("""
            SELECT cluster_id, COUNT(*) as count 
            FROM reddit_posts 
            WHERE cluster_id IS NOT NULL 
            GROUP BY cluster_id
        """)
        cluster_stats = cursor.fetchall()
        
        # If we have more balanced clusters, use keyword matching
        if len(cluster_stats) > 2:
            query_words = set(cleaned_query.lower().split())
            best_cluster = doc2vec_cluster
            best_score = 0
            
            for stat in cluster_stats:
                cluster_id = stat['cluster_id']
                
                # Get sample posts from this cluster
                cursor.execute("""
                    SELECT title, post_body_cleaned 
                    FROM reddit_posts 
                    WHERE cluster_id = %s 
                    LIMIT 10
                """, (cluster_id,))
                posts = cursor.fetchall()
                
                # Calculate keyword overlap score
                cluster_text = ' '.join([
                    (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).lower()
                    for post in posts
                ])
                cluster_words = set(cluster_text.split())
                
                # Calculate Jaccard similarity
                intersection = len(query_words.intersection(cluster_words))
                union = len(query_words.union(cluster_words))
                
                if union > 0:
                    jaccard_score = intersection / union
                    
                    # Weight smaller clusters higher to overcome imbalance
                    weight = 1.0 / (stat['count'] ** 0.3)  # Reduce influence of large clusters
                    weighted_score = jaccard_score * weight
                    
                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_cluster = cluster_id
            
            cursor.close()
            connection.close()
            return int(best_cluster)
        
        cursor.close()
        connection.close()
    
    return int(doc2vec_cluster)    