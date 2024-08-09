import spacy
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor
import os
import io
from bs4 import BeautifulSoup
import re
import requests
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
from io import BytesIO
import pandas as pd
from io import StringIO

# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")
# Tăng giới hạn max_length
nlp.max_length = 2000000
API_KEY = 'AIzaSyAQfDwx60quGbjqLeKOwk4DTl27s180cDE'
CX = 'f5a8b4e14ca474f61'

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    response = requests.get(url, verify=False)
    return response.json()

model = SentenceTransformer('dangvantuan/vietnamese-embedding')
def preprocess_text_vietnamese(text):
    # Process text with spaCy pipeline
    doc = nlp(text)
    # Filter out stopwords and punctuation, and convert to lowercase
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    # Join tokens back into a single string
    processed_text = ' '.join(tokens)
    return processed_text, tokens

def embeddind_vietnamese(text):
    embedding = model.encode(text)
    return embedding
def calculate_similarity(query_features, reference_features):
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores
def combine_lines_and_split_sentences(text):
    combined_sentences = []
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', '', text)
    text = re.sub(r'[^\w\s.,;?:]', ' ', text)
    text = text.replace('. ', '.\n')
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\ {2,}', ' ', text)
    
    lines = text.split('\n')
    for line in lines:
        sentences = re.split(r'[.?!:]', line)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                combined_sentences.append(sentence)

    return combined_sentences

def calculate_dynamic_threshold(length, max_threshold=0.9, min_threshold=0.7):
    if length < 15:
        return max_threshold
    elif length > 45:
        return min_threshold
    else:
        scaling_factor = (max_threshold - min_threshold) / (45 - 15)
        threshold = max_threshold - (length - 15) * scaling_factor
        return threshold

def extract_text_from_pdf(url, save_path):
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        return ""
    if save_path:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        pdf_path = save_path
    else:
        pdf_path = io.BytesIO(response.content)

    with fitz.open(pdf_path) as document:
        with ThreadPoolExecutor() as executor:
            text_parts = executor.map(lambda page: page.get_text("text"), document)
    
    pdf_text = ''.join(text_parts)

    if save_path:
        os.remove(save_path)
    
    return pdf_text

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def fetch_docx(url):
    response = requests.get(url)
    response.raise_for_status()  # Kiểm tra lỗi HTTP
    doc_file = BytesIO(response.content)
    doc = Document(doc_file)
    text = [para.text for para in doc.paragraphs]
    return '\n'.join(text)

def fetch_csv(url):
    response = requests.get(url)
    response.raise_for_status()  # Kiểm tra lỗi HTTP
    csv_content = StringIO(response.text)
    df = pd.read_csv(csv_content)
    return df.to_string()  # Trả về dữ liệu CSV dưới dạng chuỗi

def fetch_url(url):
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        
        if url.lower().endswith('.pdf'):
            return extract_text_from_pdf(url, 'downloaded_document.pdf')
        elif url.lower().endswith('.docx'):
            return fetch_docx(url)
        elif url.lower().endswith('.csv'):
            return fetch_csv(url)
        else:
            return extract_text_from_html(response.text)
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error accessing {url}: {e}")
        return ""