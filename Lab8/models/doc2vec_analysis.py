import os
import pandas as pd
import nltk
from dotenv import load_dotenv
from sqlalchemy import create_engine
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np

# 1. Setup and Database Connection

load_dotenv()

# The necessary NLTK data
print("Downloading NLTK data...")
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')  

def connect_to_db():
   
    print("Connecting to the database...")
    try:
        
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        db = os.getenv('DB_NAME')
        host = 'db' 
        
        engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{db}"
        engine = create_engine(engine_url)

        query = "SELECT id, post_body_cleaned FROM reddit_posts WHERE post_body_cleaned IS NOT NULL AND post_body_cleaned != ''"
        
        print("Loading data from the database...")
        df = pd.read_sql(query, engine)
        print(f"Successfully loaded {len(df)} documents.")
        return df
    except Exception as e:
        print(f"Error connecting to the database or fetching data: {e}")
        return None

# 2. Text Preprocessing

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Cleaning and tokenizing the input text."""
    if not isinstance(text, str):
        return []
    tokens = word_tokenize(text.lower())
    return [word for word in tokens if word.isalpha() and word not in stop_words]

# 3. Doc2Vec Model Training

def train_doc2vec_models(documents):
    """Doc2Vec models with different vector sizes."""
    configs = [
        {'vector_size': 50, 'min_count': 3, 'epochs': 40, 'dm': 1},
        {'vector_size': 100, 'min_count': 3, 'epochs': 40, 'dm': 1},
        {'vector_size': 150, 'min_count': 3, 'epochs': 40, 'dm': 1}
    ]
    
    results = {}
    for i, config in enumerate(configs):
        print(f"\n--- Training Model {i+1} (vector_size={config['vector_size']}) ---")
        model = Doc2Vec(documents, **config)
        vectors = [model.infer_vector(doc.words) for doc in documents]
        results[f'config_{i+1}'] = {'model': model, 'vectors': vectors, 'config': config}
    return results

#  4.Evaluation

def perform_clustering(df, doc2vec_results, num_clusters=5):
    """Performs KMeans clustering on the vectors"""
    for config_name, data in doc2vec_results.items():
        print(f"\n--- Clustering for {config_name} ---")
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(data['vectors'])
        df[f'cluster_{config_name}'] = clusters
    return df

def review_clusters(df, config_name, num_clusters=5):
    """Prints sample documents from each cluster """
    print(f"\n--- Reviewing Clusters for {config_name} ---")
    for i in range(num_clusters):
        print(f"\nCluster {i}:")
        sample_docs = df[df[f'cluster_{config_name}'] == i].sample(n=min(5, len(df[df[f'cluster_{config_name}'] == i])), replace=False)
        for text in sample_docs['post_body_cleaned']:
            print(f"  - {text[:120]}...")
        print("-" * 20)

# --- 5. Visualization ---

def create_visualizations(df, doc2vec_results, num_clusters=5):
    """t-SNE visualization of the clusters."""
    print("\n--- Generating t-SNE plot for all configurations ---")
    fig, axes = plt.subplots(1, 3, figsize=(24, 7))
    fig.suptitle('t-SNE Visualization of Doc2Vec Clusters by Vector Size', fontsize=18)

    for i, (config_name, data) in enumerate(doc2vec_results.items()):
        vectors_np = np.array(data['vectors'])

        n_samples = vectors_np.shape[0]
        perplexity_value = min(30, n_samples - 1)
        
        if n_samples > 1:
            tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity_value, max_iter=1000)
            vectors_2d = tsne.fit_transform(vectors_np)
            
            plot_df = pd.DataFrame(vectors_2d, columns=['x', 'y'])
            plot_df['cluster'] = df[f'cluster_{config_name}']
            
            vector_size = data['config']['vector_size']
            ax = axes[i]
            
            sns.scatterplot(
                data=plot_df, x='x', y='y', hue='cluster',
                palette=sns.color_palette("hsv", n_colors=num_clusters),
                legend='full', alpha=0.7, ax=ax
            )
            ax.set_title(f'Configuration {i+1} (vector_size={vector_size})')
            ax.set_xlabel('')
            ax.set_ylabel('')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('cluster_visualization.png')
    print("\nVisualization saved as 'cluster_visualization.png'")

# Main

def main():
    df = connect_to_db()
    
    if df is not None and not df.empty:
        documents = [TaggedDocument(preprocess_text(doc), [i]) for i, doc in enumerate(df['post_body_cleaned'])]
        
        doc2vec_results = train_doc2vec_models(documents)
        
        NUM_CLUSTERS = 5
        
        df_clustered = perform_clustering(df.copy(), doc2vec_results, NUM_CLUSTERS)
        
        df_clustered.to_csv('reddit_data_with_clusters.csv', index=False)
        print("\nResults with cluster assignments saved 'reddit_data_with_clusters.csv'")
        
        review_clusters(df_clustered, 'config_1', NUM_CLUSTERS)
        review_clusters(df_clustered, 'config_2', NUM_CLUSTERS)
        review_clusters(df_clustered, 'config_3', NUM_CLUSTERS)
        
        create_visualizations(df_clustered, doc2vec_results, NUM_CLUSTERS)

if __name__ == "__main__":
    main()