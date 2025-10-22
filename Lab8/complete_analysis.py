#!/usr/bin/env python3
"""
DSCI-560 Lab 8: Complete Analysis Script
Single script to run entire document embedding analysis on actual collected data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from core import db_handler

# Set style for professional visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def simple_tokenize(text):
    """Simple tokenization."""
    if not text:
        return []
    return [t.lower() for t in text.split() if t.isalpha() and len(t) > 2]

def create_tfidf_embeddings(posts, max_features=100):
    """Create TF-IDF embeddings."""
    texts = []
    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        texts.append(text)
    
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix.toarray(), vectorizer.get_feature_names_out()

def create_word_frequency_embeddings(posts, vocab_size=100):
    """Create word frequency embeddings (bag-of-words)."""
    all_words = []
    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        words = simple_tokenize(text)
        all_words.extend(words)
    
    word_counts = Counter(all_words)
    vocab = [word for word, count in word_counts.most_common(vocab_size)]
    word_to_idx = {word: i for i, word in enumerate(vocab)}
    
    embeddings = []
    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        words = simple_tokenize(text)
        
        freq_vector = [0] * vocab_size
        total_words = 0
        
        for word in words:
            if word in word_to_idx:
                freq_vector[word_to_idx[word]] += 1
                total_words += 1
        
        if total_words > 0:
            freq_vector = [count / total_words for count in freq_vector]
        
        embeddings.append(freq_vector)
    
    return np.array(embeddings), vocab

def evaluate_clustering(embeddings, max_k=10):
    """Evaluate clustering quality using silhouette scores."""
    if len(embeddings) < 2:
        return 0, 2
    
    max_k = min(max_k, len(embeddings) - 1)
    best_score = -1
    best_k = 2
    
    for k in range(2, max_k + 1):
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            
            if score > best_score:
                best_score = score
                best_k = k
        except:
            continue
    
    return best_score, best_k

def create_tsne_visualization(embeddings, labels, method_name, dimension, filename):
    """Create enhanced t-SNE visualization."""
    try:
        if len(embeddings) < 4:
            print(f"Not enough data for {method_name} visualization")
            return
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Apply t-SNE
        tsne = TSNE(n_components=2, random_state=42, init='pca', perplexity=30, n_iter=1000)
        embeddings_2d = tsne.fit_transform(embeddings)
        
        # Get unique labels and create color map
        unique_labels = np.unique(labels)
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
        
        # Plot each cluster
        for i, label in enumerate(unique_labels):
            mask = labels == label
            ax.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                      c=[colors[i]], label=f'Cluster {label}', 
                      s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        # Enhanced styling
        ax.set_title(f'{method_name} Embeddings (dim={dimension})\nClustering Visualization', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('t-SNE Component 1', fontsize=12, fontweight='bold')
        ax.set_ylabel('t-SNE Component 2', fontsize=12, fontweight='bold')
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        # Add statistics
        stats_text = f'Total Points: {len(embeddings)}\nClusters: {len(unique_labels)}\nDimension: {dimension}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved visualization: {filename}")
    except Exception as e:
        print(f"Error creating visualization for {method_name}: {e}")

def create_keyword_analysis(posts, labels, method_name, dimension):
    """Create keyword analysis for each cluster."""
    clusters = defaultdict(list)
    for i, post in enumerate(posts):
        clusters[labels[i]].append(post)
    
    print(f"\n{method_name} Cluster Analysis (dim={dimension}):")
    print("-" * 60)
    
    cluster_sizes = [len(clusters[i]) for i in range(len(clusters))]
    print(f"Total clusters: {len(clusters)}")
    print(f"Cluster sizes: {cluster_sizes}")
    print(f"Size distribution: min={min(cluster_sizes)}, max={max(cluster_sizes)}, avg={np.mean(cluster_sizes):.1f}")
    
    for cluster_id, cluster_posts in clusters.items():
        print(f"\nCluster {cluster_id}: {len(cluster_posts)} posts")
        
        # Get common words in this cluster
        all_text = ' '.join([
            (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
            for post in cluster_posts
        ])
        
        words = simple_tokenize(all_text)
        word_counts = Counter(words)
        
        # Filter common words
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'oil', 'sit', 'try', 'use', 'want', 'will', 'with', 'this', 'that', 'have', 'been', 'they', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'}
        
        keywords = []
        for word, count in word_counts.most_common(20):
            if word not in common_words and len(word) > 3:
                keywords.append(f"{word}({count})")
                if len(keywords) >= 8:
                    break
        
        if keywords:
            print(f"  Keywords: {', '.join(keywords)}")
        
        # Show sample titles
        sample_titles = [post.get('title', 'No title')[:60] + '...' 
                        for post in cluster_posts[:3] if post.get('title')]
        for title in sample_titles:
            print(f"  - {title}")

def create_keyword_plot(posts, labels, method_name, dimension, cluster_id):
    """Create keyword frequency plot for a specific cluster."""
    clusters = defaultdict(list)
    for i, post in enumerate(posts):
        clusters[labels[i]].append(post)
    
    if cluster_id not in clusters:
        return
    
    cluster_posts = clusters[cluster_id]
    
    # Combine all text in cluster
    all_text = ' '.join([
        (post.get('title', '') + ' ' + post.get('post_body_cleaned', '')).strip()
        for post in cluster_posts
    ])
    
    if not all_text.strip():
        return
    
    # Get word frequencies
    words = simple_tokenize(all_text)
    word_counts = Counter(words)
    
    # Filter common words
    common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'oil', 'sit', 'try', 'use', 'want', 'will', 'with', 'this', 'that', 'have', 'been', 'they', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'}
    
    # Get top keywords
    keywords = []
    counts = []
    for word, count in word_counts.most_common(20):
        if word not in common_words and len(word) > 3:
            keywords.append(word)
            counts.append(count)
            if len(keywords) >= 10:
                break
    
    if not keywords:
        return
    
    # Create horizontal bar plot
    plt.figure(figsize=(10, 6))
    bars = plt.barh(keywords, counts, color=plt.cm.viridis(np.linspace(0, 1, len(keywords))))
    plt.title(f'{method_name} Cluster {cluster_id} Top Keywords (dim={dimension})', 
             fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Frequency', fontsize=12)
    plt.ylabel('Keywords', fontsize=12)
    
    # Add value labels
    for bar, count in zip(bars, counts):
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{count}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    filename = f"visualizations/{method_name.lower().replace(' ', '_')}_cluster_{cluster_id}_keywords_dim{dimension}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved keyword plot: {filename}")

def create_distribution_plot(posts, labels, method_name, dimension):
    """Create cluster distribution visualization."""
    clusters = defaultdict(list)
    for i, post in enumerate(posts):
        clusters[labels[i]].append(post)
    
    cluster_sizes = [len(clusters[i]) for i in range(len(clusters))]
    cluster_ids = list(range(len(clusters)))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar chart
    bars = ax1.bar(cluster_ids, cluster_sizes, color=plt.cm.Set3(np.linspace(0, 1, len(clusters))), 
                   alpha=0.8, edgecolor='black')
    ax1.set_title(f'{method_name} Cluster Size Distribution (dim={dimension})', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Cluster ID', fontsize=12)
    ax1.set_ylabel('Number of Posts', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, size in zip(bars, cluster_sizes):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{size}', ha='center', va='bottom', fontweight='bold')
    
    # Pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(clusters)))
    wedges, texts, autotexts = ax2.pie(cluster_sizes, labels=[f'Cluster {i}' for i in cluster_ids], 
                                       autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title(f'{method_name} Cluster Distribution (dim={dimension})', 
                  fontsize=14, fontweight='bold')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    plt.tight_layout()
    filename = f"visualizations/{method_name.lower().replace(' ', '_')}_distribution_dim{dimension}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved distribution plot: {filename}")

def create_comprehensive_comparison(results_data, filename):
    """Create comprehensive comparison plot."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Extract data
    methods = [r['method'] for r in results_data]
    dimensions = [r['dimension'] for r in results_data]
    scores = [r['silhouette_score'] for r in results_data]
    clusters = [r['optimal_clusters'] for r in results_data]
    
    # Plot 1: Silhouette Scores by Dimension
    unique_dims = sorted(set(dimensions))
    tfidf_scores = [scores[i] for i, d in enumerate(dimensions) if methods[i] == 'TF-IDF']
    freq_scores = [scores[i] for i, d in enumerate(dimensions) if methods[i] == 'Word Frequency']
    
    ax1.plot(unique_dims, tfidf_scores, 'o-', label='TF-IDF (Doc2Vec)', linewidth=3, markersize=8)
    ax1.plot(unique_dims, freq_scores, 's-', label='Word Frequency (WordBins)', linewidth=3, markersize=8)
    ax1.set_title('Silhouette Scores Across Dimensions', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Embedding Dimension', fontsize=12)
    ax1.set_ylabel('Silhouette Score', fontsize=12)
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, max(max(tfidf_scores), max(freq_scores)) * 1.1)
    
    # Plot 2: Optimal Clusters by Dimension
    tfidf_clusters = [clusters[i] for i, d in enumerate(dimensions) if methods[i] == 'TF-IDF']
    freq_clusters = [clusters[i] for i, d in enumerate(dimensions) if methods[i] == 'Word Frequency']
    
    ax2.plot(unique_dims, tfidf_clusters, 'o-', label='TF-IDF (Doc2Vec)', linewidth=3, markersize=8)
    ax2.plot(unique_dims, freq_clusters, 's-', label='Word Frequency (WordBins)', linewidth=3, markersize=8)
    ax2.set_title('Optimal Number of Clusters', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Embedding Dimension', fontsize=12)
    ax2.set_ylabel('Number of Clusters', fontsize=12)
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Method Performance Comparison
    method_avg_scores = {}
    for method in set(methods):
        method_scores = [scores[i] for i, m in enumerate(methods) if m == method]
        method_avg_scores[method] = np.mean(method_scores)
    
    bars = ax3.bar(method_avg_scores.keys(), method_avg_scores.values(), 
                   color=['skyblue', 'lightcoral'], alpha=0.8, edgecolor='black')
    ax3.set_title('Average Performance by Method', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Average Silhouette Score', fontsize=12)
    ax3.set_ylim(0, max(method_avg_scores.values()) * 1.1)
    
    for bar, score in zip(bars, method_avg_scores.values()):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 4: Summary Statistics Table
    ax4.axis('off')
    
    summary_data = []
    for dim in unique_dims:
        tfidf_idx = next(i for i, d in enumerate(dimensions) if d == dim and methods[i] == 'TF-IDF')
        freq_idx = next(i for i, d in enumerate(dimensions) if d == dim and methods[i] == 'Word Frequency')
        
        summary_data.append([
            f"Dim {dim}",
            f"{scores[tfidf_idx]:.3f}",
            f"{clusters[tfidf_idx]}",
            f"{scores[freq_idx]:.3f}",
            f"{clusters[freq_idx]}"
        ])
    
    table = ax4.table(cellText=summary_data,
                     colLabels=['Dimension', 'TF-IDF Score', 'TF-IDF Clusters', 
                               'Word Freq Score', 'Word Freq Clusters'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    for i in range(len(summary_data) + 1):
        for j in range(5):
            cell = table[(i, j)]
            if i == 0:
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
    
    ax4.set_title('Performance Summary Table', fontsize=14, fontweight='bold', pad=20)
    
    plt.suptitle('DSCI-560 Lab 8: Comprehensive Embedding Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Saved comprehensive comparison: {filename}")

def main():
    """Complete analysis pipeline."""
    print("DSCI-560 Lab 8: Complete Document Embedding Analysis")
    print("=" * 70)
    
    # Load actual collected data
    print("Loading data from database...")
    conn = db_handler.create_connection()
    if not conn:
        print("ERROR: Could not connect to database")
        print("Please ensure MySQL is running and credentials are correct in .env file")
        return
    
    posts = db_handler.fetch_cleaned_posts(conn)
    conn.close()
    
    if not posts:
        print("ERROR: No cleaned posts found")
        print("Please run data collection and preprocessing first")
        return
    
    print(f"Successfully loaded {len(posts)} posts from database")
    
    # Create visualizations directory
    vis_dir = Path("visualizations")
    vis_dir.mkdir(exist_ok=True)
    
    # Test different dimensions
    dimensions = [50, 100, 150]
    all_results = []
    
    print(f"\nAnalyzing {len(posts)} posts across {len(dimensions)} dimensions...")
    
    for dim in dimensions:
        print(f"\nProcessing dimension {dim}...")
        
        # Use all available posts for analysis
        analysis_posts = posts
        
        # Method 1: TF-IDF Embeddings (Doc2Vec equivalent)
        print(f"  Creating TF-IDF embeddings (dim={dim})...")
        tfidf_embeddings, tfidf_features = create_tfidf_embeddings(analysis_posts, max_features=dim)
        tfidf_score, tfidf_k = evaluate_clustering(tfidf_embeddings)
        
        # Cluster TF-IDF embeddings
        kmeans_tfidf = KMeans(n_clusters=tfidf_k, random_state=42, n_init=10)
        tfidf_labels = kmeans_tfidf.fit_predict(tfidf_embeddings)
        
        # Create t-SNE visualization
        create_tsne_visualization(
            tfidf_embeddings, tfidf_labels, 
            "Doc2Vec", dim, 
            f"visualizations/doc2vec_dim{dim}_tsne.png"
        )
        
        # Method 2: Word Frequency Embeddings (WordBins)
        print(f"  Creating Word Frequency embeddings (dim={dim})...")
        freq_embeddings, freq_vocab = create_word_frequency_embeddings(analysis_posts, vocab_size=dim)
        freq_score, freq_k = evaluate_clustering(freq_embeddings)
        
        # Cluster frequency embeddings
        kmeans_freq = KMeans(n_clusters=freq_k, random_state=42, n_init=10)
        freq_labels = kmeans_freq.fit_predict(freq_embeddings)
        
        # Create t-SNE visualization
        create_tsne_visualization(
            freq_embeddings, freq_labels, 
            "WordBins", dim, 
            f"visualizations/wordbins_dim{dim}_tsne.png"
        )
        
        # Store results
        all_results.extend([
            {
                'method': 'TF-IDF',
                'dimension': dim,
                'silhouette_score': tfidf_score,
                'optimal_clusters': tfidf_k,
                'total_posts': len(analysis_posts)
            },
            {
                'method': 'Word Frequency',
                'dimension': dim,
                'silhouette_score': freq_score,
                'optimal_clusters': freq_k,
                'total_posts': len(analysis_posts)
            }
        ])
        
        print(f"    TF-IDF: score={tfidf_score:.3f}, k={tfidf_k}")
        print(f"    Word Frequency: score={freq_score:.3f}, k={freq_k}")
    
    # Detailed analysis for best dimension
    best_dim = 100
    print(f"\nDetailed Analysis for dimension {best_dim}:")
    print("=" * 60)
    
    # TF-IDF detailed analysis
    tfidf_embeddings, tfidf_features = create_tfidf_embeddings(posts, max_features=best_dim)
    tfidf_score, tfidf_k = evaluate_clustering(tfidf_embeddings)
    kmeans_tfidf = KMeans(n_clusters=tfidf_k, random_state=42, n_init=10)
    tfidf_labels = kmeans_tfidf.fit_predict(tfidf_embeddings)
    
    create_keyword_analysis(posts, tfidf_labels, "TF-IDF", best_dim)
    
    # Create keyword plots for TF-IDF clusters
    for cluster_id in range(tfidf_k):
        create_keyword_plot(posts, tfidf_labels, "Doc2Vec", best_dim, cluster_id)
    
    # Create distribution plot for TF-IDF
    create_distribution_plot(posts, tfidf_labels, "Doc2Vec", best_dim)
    
    # Word Frequency detailed analysis
    freq_embeddings, freq_vocab = create_word_frequency_embeddings(posts, vocab_size=best_dim)
    freq_score, freq_k = evaluate_clustering(freq_embeddings)
    kmeans_freq = KMeans(n_clusters=freq_k, random_state=42, n_init=10)
    freq_labels = kmeans_freq.fit_predict(freq_embeddings)
    
    create_keyword_analysis(posts, freq_labels, "Word Frequency", best_dim)
    
    # Create keyword plots for Word Frequency clusters
    for cluster_id in range(freq_k):
        create_keyword_plot(posts, freq_labels, "WordBins", best_dim, cluster_id)
    
    # Create distribution plot for Word Frequency
    create_distribution_plot(posts, freq_labels, "WordBins", best_dim)
    
    # Create comprehensive comparison
    create_comprehensive_comparison(all_results, "visualizations/comprehensive_analysis.png")
    
    # Save results
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('visualizations/complete_results.csv', index=False)
    
    # Final summary
    print(f"\nFINAL RESULTS SUMMARY")
    print("=" * 50)
    
    best_tfidf_score = max([r['silhouette_score'] for r in all_results if r['method'] == 'TF-IDF'])
    best_freq_score = max([r['silhouette_score'] for r in all_results if r['method'] == 'Word Frequency'])
    
    print(f"Best TF-IDF Performance: {best_tfidf_score:.3f}")
    print(f"Best Word Frequency Performance: {best_freq_score:.3f}")
    
    if best_tfidf_score > best_freq_score:
        print(f"\nWINNER: TF-IDF Method")
        print("Advantages: Better semantic understanding, handles rare words well")
        print("Disadvantages: Higher computational cost, more complex")
    else:
        print(f"\nWINNER: Word Frequency Method")
        print("Advantages: Simple, fast, interpretable")
        print("Disadvantages: Less semantic understanding, sensitive to word frequency")
    
    print(f"\nResults saved to visualizations/complete_results.csv")
    print("\nAnalysis completed successfully!")
    print("\nGenerated visualizations:")
    print("- doc2vec_dim50_tsne.png, doc2vec_dim100_tsne.png, doc2vec_dim150_tsne.png")
    print("- wordbins_dim50_tsne.png, wordbins_dim100_tsne.png, wordbins_dim150_tsne.png")
    print("- comprehensive_analysis.png (complete comparison)")
    print("- Cluster keyword plots and distribution analysis")
    print(f"\nTotal visualizations generated: {len(list(vis_dir.glob('*.png')))}")

if __name__ == '__main__':
    main()
