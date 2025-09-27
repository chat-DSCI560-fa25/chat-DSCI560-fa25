# Lab5/core/db_handler.py

import mysql.connector
from mysql.connector import Error
import config
import numpy as np


def create_connection():
    """Teh database connection."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        if connection.is_connected():
            print("Successfully connected to the database.")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    return connection

def create_table(connection):
    """Create the reddit_posts table incase its not there!"""
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS reddit_posts (
        id VARCHAR(20) PRIMARY KEY,
        subreddit VARCHAR(50),
        title TEXT,
        author_masked VARCHAR(100),
        created_utc DATETIME,
        post_body_raw MEDIUMTEXT,
        post_body_cleaned MEDIUMTEXT NULL,
        image_text MEDIUMTEXT NULL,
        keywords TEXT NULL,
        embedding_vector BLOB NULL,
        cluster_id INT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'reddit_posts' is ready.")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

def insert_post(connection, post_data):
    cursor = connection.cursor()
    insert_query = """
    INSERT IGNORE INTO reddit_posts (id, subreddit, title, author_masked, created_utc, post_body_raw)
    VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s), %s)
    """
    try:
        cursor.execute(insert_query, post_data)
        connection.commit()
    except Error as e:
        print(f"Error inserting post {post_data[0]}: {e}")
    finally:
        cursor.close()

 """All posts that have not been cleaned yet."""
def fetch_unprocessed_posts(connection):
   
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id,title, post_body_raw FROM reddit_posts WHERE post_body_cleaned IS NULL"
    try:
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts
    except Error as e:
        print(f"Error fetching unprocessed posts: {e}")
        return []
    finally:
        cursor.close()

def update_cleaned_post(connection, post_id, cleaned_text):
    cursor = connection.cursor()
    query = "UPDATE reddit_posts SET post_body_cleaned = %s WHERE id = %s"
    try:
        cursor.execute(query, (cleaned_text, post_id))
        connection.commit()
    except Error as e:
        print(f"Error updating post {post_id}: {e}")
    finally:
        cursor.close()        

def fetch_cleaned_posts(connection):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id, post_body_cleaned FROM reddit_posts WHERE post_body_cleaned IS NOT NULL AND embedding_vector IS NULL"
    try:
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts
    except Error as e:
        print(f"Error fetching cleaned posts: {e}")
        return []
    finally:
        cursor.close()

def update_post_analysis(connection, post_id, vector, cluster_id):
    cursor = connection.cursor()
    vector_bytes = vector.tobytes()
    query = "UPDATE reddit_posts SET embedding_vector = %s, cluster_id = %s WHERE id = %s"
    try:
        cursor.execute(query, (vector_bytes, int(cluster_id), post_id))
        connection.commit()
    except Error as e:
        print(f"Error updating post analysis for {post_id}: {e}")
    finally:
        cursor.close()        


"""Fetches all posts that have a cluster_id."""
def fetch_all_analyzed_posts(connection):
  
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id, title, cluster_id, embedding_vector FROM reddit_posts WHERE cluster_id IS NOT NULL"
    try:
        cursor.execute(query)
        posts = cursor.fetchall()
        # Convert BLOB vector back to numpy array
        for post in posts:
            post['embedding_vector'] = np.frombuffer(post['embedding_vector'], dtype=np.float32)
        return posts
    except Error as e:
        print(f"Error fetching analyzed posts: {e}")
        return []
    finally:
        cursor.close()        



def fetch_posts_by_cluster(connection, cluster_id):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT title FROM reddit_posts WHERE cluster_id = %s LIMIT 10"
    try:
        cursor.execute(query, (cluster_id,))
        posts = cursor.fetchall()
        return posts
    except Error as e:
        print(f"Error fetching posts for cluster {cluster_id}: {e}")
        return []
    finally:
        cursor.close()        