
from flask import Flask, render_template, request
import sys
sys.path.append('..')
from core import analysis, db_handler

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        # Get the user's query from the form
        query = request.form['query']
        
        # Use our existing backend functions to get the results
        cluster_id = analysis.find_matching_cluster(query)
        if cluster_id is not None:
            connection = db_handler.create_connection()
            posts = db_handler.fetch_posts_by_cluster(connection, cluster_id)
            connection.close()
            results = {
                'cluster_id': cluster_id,
                'posts': posts
            }
            
    # Render the HTML page, passing in the results if they exist
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)