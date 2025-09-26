import re, pytesseract
from bs4 import BeautifulSoup
from PIL import Image
from collections import Counter

from bs4 import MarkupResemblesLocatorWarning
import warnings
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words("english"))
except LookupError:
    import nltk
    nltk.download("stopwords")
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words("english"))

def clean_text(text):
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    return " ".join([w for w in text.split() if w.lower() not in stop_words])

def mask_username(username):
    return f"user_{hash(username) % 10000}" if username else "anon"

def extract_keywords(text, top_n=5):
    words = [w.lower() for w in text.split() if w.lower() not in stop_words]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]

def extract_ocr(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception:
        return ""
