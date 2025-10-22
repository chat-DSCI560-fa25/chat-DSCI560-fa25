#!/usr/bin/env python3
"""
Compare Word2Vec-binned frequency vectors vs Doc2Vec embeddings.
Produces silhouette scores for clustering quality at three embedding dimensions.

Usage:
    python3 lab5/scripts/word2vec_binning_compare.py

This script connects to the project's DB (uses lab5/config.py or .env fallback),
loads cleaned posts, builds Word2Vec on the token corpus, clusters word vectors
into K bins (K equals desired embedding dimension), converts each document into
an L1-normalized histogram across bins (word-frequency per bin), and runs KMeans
on these document vectors. It also trains Doc2Vec models for the same
vector sizes and compares silhouette scores.

Note: Training can be slow depending on data size. Adjust parameters for speed.
"""
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# reuse the project's preprocessor/db logic if available
SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

# Import config and DB handler
try:
    import config
except Exception:
    # fallback to parsing .env
    def _parse_env(path):
        data = {}
        for ln in path.read_text().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            data[k] = v
        return data

    env = _parse_env(SCRIPT_DIR / '.env')
    class _C: pass
    config = _C()
    config.DB_HOST = env.get('DB_HOST')
    config.DB_USER = env.get('DB_USER')
    config.DB_PASSWORD = env.get('DB_PASSWORD')
    config.DB_NAME = env.get('DB_NAME')

# Ensure modules that import `config` will get our fallback
import types
sys.modules['config'] = types.SimpleNamespace(**{
    'DB_HOST': config.DB_HOST,
    'DB_USER': config.DB_USER,
    'DB_PASSWORD': config.DB_PASSWORD,
    'DB_NAME': config.DB_NAME,
})

from core import db_handler, preprocessor

import numpy as np
from gensim.models import Word2Vec, Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def fetch_cleaned_posts():
    conn = db_handler.create_connection()
    if not conn:
        raise RuntimeError('Could not connect to DB')
    posts = db_handler.fetch_cleaned_posts(conn)
    conn.close()
    return posts


def tokenize_post(text):
    if not text:
        return []
    # lightweight tokenization consistent with preprocessor
    return [t for t in text.lower().split() if t.isalpha() and len(t) > 2]


def build_word2vec(corpus, vector_size=100, window=5, min_count=2, epochs=20):
    model = Word2Vec(sentences=corpus, vector_size=vector_size, window=window, min_count=min_count, workers=4)
    model.train(corpus, total_examples=len(corpus), epochs=epochs)
    return model


def cluster_word_vectors(word_vectors, k):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(word_vectors)
    return km, labels


def doc_to_bin_hist(tokens, word2vec_model, word_to_bin, k):
    bins = [0] * k
    total = 0
    for w in tokens:
        if w in word_to_bin:
            bins[word_to_bin[w]] += 1
            total += 1
    if total == 0:
        return np.zeros(k, dtype=float)
    return np.array(bins, dtype=float) / float(total)


def train_doc2vec(tagged_docs, vector_size=50, epochs=40):
    model = Doc2Vec(vector_size=vector_size, window=5, min_count=1, workers=4, epochs=epochs, dm=0)
    model.build_vocab(tagged_docs)
    model.train(tagged_docs, total_examples=len(tagged_docs), epochs=epochs)
    return model


def evaluate_embeddings(embeddings, min_k=2, max_k=10):
    # choose k for clustering; ensure k < n_samples
    n = len(embeddings)
    if n < 2:
        return None
    max_k = min(max_k, n-1)
    best = None
    for k in range(min_k, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(embeddings)
        try:
            score = silhouette_score(embeddings, labels)
        except Exception:
            score = -1
        if best is None or score > best[0]:
            best = (score, k)
    return best


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compare Word2Vec-binned vectors vs Doc2Vec embeddings')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of posts to use (quick test)')
    parser.add_argument('--dims', type=int, nargs='+', default=[50,100,150], help='Dimensions to evaluate')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    np.random.seed(args.seed)

    posts = fetch_cleaned_posts()
    if not posts:
        logging.error('No cleaned posts found in DB. Run preprocessor first.')
        return
    if args.limit:
        posts = posts[:args.limit]

    # build corpus
    corpus = []
    docs_text = []
    for p in posts:
        text = (p.get('title', '') + ' ' + p.get('post_body_cleaned', '')).strip()
        toks = tokenize_post(text)
        corpus.append(toks)
        docs_text.append((toks, p['id']))

    logging.info(f'Built corpus with {len(corpus)} documents and vocab size approx {sum(len(s) for s in corpus)} tokens')

    # dimensions to compare (use the same three used in doc2vec experiments; if not known, [50,100,150])
    dims = args.dims

    results = []

    for dim in dims:
        logging.info(f'--- Processing dimension {dim} ---')

        # 1) Word2Vec + clustering words into dim bins
        logging.info('Training Word2Vec...')
        w2v = build_word2vec(corpus, vector_size=dim, epochs=30)

        vocab = [w for w in w2v.wv.index_to_key]
        word_vecs = np.array([w2v.wv[w] for w in vocab])

        logging.info('Clustering word vectors into bins...')
        kmeans_words = KMeans(n_clusters=dim, random_state=42, n_init=10).fit(word_vecs)
        word_to_bin = {w: int(lbl) for w, lbl in zip(vocab, kmeans_words.labels_)}

        # convert each doc to bin-hist normalized vector
        doc_vectors_wordbins = np.array([doc_to_bin_hist(toks, w2v, word_to_bin, dim) for toks, _ in docs_text])

        # evaluate clustering quality on these doc vectors
        best_wordbins = evaluate_embeddings(doc_vectors_wordbins)
        logging.info(f'Word-bins best silhouette: {best_wordbins}')

        # 2) Doc2Vec embeddings of same dimension
        logging.info('Training Doc2Vec...')
        tagged = [TaggedDocument(words=toks, tags=[i]) for i, (toks, _) in enumerate(docs_text)]
        d2v = train_doc2vec(tagged, vector_size=dim, epochs=40)
        doc_vectors_d2v = np.array([d2v.infer_vector(toks) for toks, _ in docs_text])

        best_d2v = evaluate_embeddings(doc_vectors_d2v)
        logging.info(f'Doc2Vec best silhouette: {best_d2v}')

        results.append((dim, best_wordbins, best_d2v))

    # Print summary
    print('\n=== SUMMARY ===')
    for dim, wb, d2v in results:
        print(f'DIM={dim}: WordBins silhouette={wb} | Doc2Vec silhouette={d2v}')

if __name__ == '__main__':
    main()
