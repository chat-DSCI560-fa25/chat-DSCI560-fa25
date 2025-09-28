# flask_app/app.py

from flask import Flask, render_template, request
import sys

sys.path.append('..')
from core import analysis, db_handler

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        query = request.form['query']
        cluster_id = analysis.find_matching_cluster(query)
        if cluster_id is not None:
            connection = db_handler.create_connection()
            posts = db_handler.fetch_posts_by_cluster(connection, cluster_id)
            connection.close()
            results = {'cluster_id': cluster_id, 'posts': posts}
            
    return render_template('index.html', results=results)