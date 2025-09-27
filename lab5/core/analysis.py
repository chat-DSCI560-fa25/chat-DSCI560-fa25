import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from core import db_handler
from scipy.spatial import distance
import pickle 


"""I am trying to train a model, that generates embeddings, and clusters the posts."""
def run_analysis():
   
    print("Starting analysis...")
    connection = db_handler.create_connection()
    if not connection:
        return

    posts = db_handler.fetch_cleaned_posts(connection)
    if not posts or len(posts) < 5:
        print("Not enough new posts to analyze.")
        connection.close()
        return

    print(f"Found {len(posts)} posts to analyze.")
    documents = [TaggedDocument(doc['post_body_cleaned'].split(), [i]) for i, doc in enumerate(posts)]

    model = Doc2Vec(documents, vector_size=50, window=5, min_count=2, workers=4, epochs=40)
    model.save("models/doc2vec.model")  # <--- THIS LINE SAVES THE DOC2VEC MODEL
    print("Doc2Vec model trained and saved.")

    vectors = [model.infer_vector(doc['post_body_cleaned'].split()) for doc in posts]
    
    num_clusters = 5
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    kmeans.fit(vectors)
    with open("models/kmeans.pkl", "wb") as f:
        pickle.dump(kmeans, f)  # <--- THIS LINE SAVES THE KMEANS MODEL
    print(f"K-Means clustering complete and model saved.")

    for i, post in enumerate(posts):
        post_id = post['id']
        vector = vectors[i]
        cluster_id = kmeans.labels_[i]
        db_handler.update_post_analysis(connection, post_id, vector, cluster_id)
        print(f"Updated post {post_id} with vector and cluster ID {cluster_id}")

    print("Analysis finished.")
    connection.close()


def interpret_clusters():
 
    print("Interpreting clusters...")
    try:
       
        with open("models/kmeans.pkl", "rb") as f:
            kmeans = pickle.load(f)
        print("KMeans model loaded.")

    except FileNotFoundError:
        print("Model files not found. Please run the analysis first with --analyze.")
        return

    connection = db_handler.create_connection()
    if not connection: return

    posts = db_handler.fetch_all_analyzed_posts(connection)
    if not posts:
        print("No analyzed posts found in the database.")
        connection.close()
        return
    
    # Group posts by clusterrr!
    clusters = {}
    for post in posts:
        cluster_id = post['cluster_id']
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(post)

    
    centroids = kmeans.cluster_centers_
    
    for cluster_id, centroid in enumerate(centroids):
        print(f"\n--- Cluster {cluster_id} ---")
        
        
        cluster_posts = clusters.get(cluster_id, [])
        if not cluster_posts:
            print("No posts in this cluster.")
            continue
            
        
        post_vectors = np.array([post['embedding_vector'] for post in cluster_posts])
        distances = distance.cdist(post_vectors, [centroid], 'euclidean').flatten()
        
        
        closest_indices = distances.argsort()[:5]
        
        print("Top 5 most representative posts:")
        for index in closest_indices:
            print(f"  - {cluster_posts[index]['title']}")
            
    connection.close()    

def find_matching_cluster(query_text):
  
    try:
        
        model = Doc2Vec.load("models/doc2vec.model")
        with open("models/kmeans.pkl", "rb") as f:
            kmeans = pickle.load(f)
    except FileNotFoundError:
        print("Model files not found. Please run --analyze first.")
        return None


    from .preprocessor import clean_text
    cleaned_query = clean_text(query_text)
    
    
    vector = model.infer_vector(cleaned_query.split())
    predicted_cluster = kmeans.predict([vector])[0]
    
    return int(predicted_cluster)    