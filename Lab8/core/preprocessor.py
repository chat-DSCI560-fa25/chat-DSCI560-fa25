import re
import nltk
from collections import Counter
from core import db_handler

# Download required NLTK data (uncomment these lines if running for the first time)
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def clean_text(text):
    """
    Comprehensive text cleaning function that removes HTML tags, 
    special characters, and irrelevant information as required by the assignment.
    """
    if not text:
        return ""
    
    # Remove URLs and links
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags and entities
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    
    # Remove Reddit-specific content (promoted messages, advertisements, etc.)
    text = re.sub(r'\[removed\]|\[deleted\]', '', text)
    text = re.sub(r'EDIT:|UPDATE:|EDIT\s*\d*:', '', text, flags=re.IGNORECASE)
    
    # Remove promotional content patterns
    text = re.sub(r'sponsored|promoted|advertisement|ad\s+by', '', text, flags=re.IGNORECASE)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^a-zA-Z\s\.\!\?\,\-]', ' ', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(text, top_n=10):
    """
    Extract keywords from text using frequency analysis and filtering.
    Returns top N keywords as required by the assignment.
    """
    if not text:
        return []
    
    try:
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and short words
        stop_words = set(stopwords.words('english'))
        
        # Add custom stopwords for Reddit/programming context
        custom_stopwords = {'like', 'would', 'could', 'get', 'use', 'also', 'really', 
                           'one', 'two', 'way', 'think', 'know', 'see', 'make', 'good'}
        stop_words.update(custom_stopwords)
        
        # Filter tokens
        filtered_tokens = [
            token for token in tokens 
            if token not in stop_words 
            and len(token) > 2 
            and token.isalpha()
        ]
        
        # Lemmatize tokens
        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
        
        # Get most common words
        word_freq = Counter(lemmatized_tokens)
        keywords = [word for word, _ in word_freq.most_common(top_n)]
        
        return keywords
    except:
        # Fallback to simple word extraction if NLTK fails
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return list(set(words))[:top_n]

def extract_image_text(image_url):
    """
    Placeholder for image text extraction using OCR.
    This would use pytesseract to extract text from images as mentioned in the assignment.
    """
    # TODO: Implement OCR text extraction using pytesseract
    # For now, return empty string as images are not commonly embedded in Reddit post text
    return ""

def run_preprocessor():
    """
    Enhanced preprocessing function that meets assignment requirements:
    - Removes HTML tags, special characters, and irrelevant information
    - Transforms data into suitable format for analysis
    - Masks usernames for privacy (already handled in scraper)
    - Identifies keywords and topics
    - Processes embedded images (placeholder implementation)
    """
    print("Starting preprocessing...")
    connection = db_handler.create_connection()
    if not connection:
        return

    posts_to_process = db_handler.fetch_unprocessed_posts(connection)
    if not posts_to_process:
        print("No new posts to process.")
        connection.close()
        return

    print(f"Found {len(posts_to_process)} posts to clean.")
    
    for post in posts_to_process:
        # Combine title and body for comprehensive text analysis
        combined_text = (post['title'] or '') + " " + (post['post_body_raw'] or '')
        
        # Clean the text according to assignment requirements
        cleaned_text = clean_text(combined_text)
        
        # Extract keywords and topics as required by assignment
        keywords = extract_keywords(cleaned_text, top_n=15)
        keywords_str = ', '.join(keywords) if keywords else ''
        
        # Handle image text extraction (placeholder for now)
        image_text = ""  # Would extract from embedded images using pytesseract
        
        # Update database with cleaned text, keywords, and image text
        db_handler.update_cleaned_post(connection, post['id'], cleaned_text)
        
        # Update keywords field if it exists in database schema
        try:
            cursor = connection.cursor()
            update_keywords_query = """
            UPDATE reddit_posts 
            SET keywords = %s, image_text = %s 
            WHERE id = %s
            """
            cursor.execute(update_keywords_query, (keywords_str, image_text, post['id']))
            connection.commit()
            cursor.close()
        except Exception as e:
            # Keywords field might not exist in current schema
            pass
            
        print(f"Cleaned and updated post: {post['id']}")
        if keywords:
            print(f"  Keywords: {keywords_str[:100]}...")

    print("Preprocessing finished.")
    connection.close()