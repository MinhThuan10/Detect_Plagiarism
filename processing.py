import spacy
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor
import os
import io
from bs4 import BeautifulSoup
import requests
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
from io import BytesIO
import pandas as pd
from io import StringIO
import spacy
from elasticsearch import Elasticsearch
import json
import torch
from sentence_split import *
# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")
# Tăng giới hạn max_length
nlp.max_length = 2000000

API_KEYS = [
    'AIzaSyAuWuy0Up52QUeKU-iYb7pNtZgu09rHk3g',
    'AIzaSyAQfDwx60quGbjqLeKOwk4DTl27s180cDE',
    'AIzaSyBf9wrYHM4SYW9w-jvA-PIIF-VJKI4owaA',
    'AIzaSyBU5mrYJLK3cGAuG3hlSDHsDFgZoWDauQM',
    'AIzaSyAn3PKdLNNuy6dc2zUcPnRiXuiSYFmLrpg',
    'AIzaSyATVTCw6KpsRrTpot-B8M5ON0J06uULkD4'
]
CX = 'f5a8b4e14ca474f61'

# Khởi tạo API Key hiện tại
current_api_key_index = 0

def get_current_api_key():
    return API_KEYS[current_api_key_index]

def get_next_api_key():
    global current_api_key_index
    current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
    return get_current_api_key()

def search_google(query):
    global current_api_key_index
    while True:
        api_key = get_current_api_key()
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={CX}"
        response = requests.get(url, verify=False)
        
        if response.status_code == 200:
            return response.json()  # Trả về dữ liệu khi yêu cầu thành công
        else:
            print(f"Yêu cầu không thành công với API Key {api_key}. Mã lỗi: {response.status_code}")
            if response.status_code == 403:
                print(f"API Key {api_key} có thể đã hết hạn. Chuyển sang key khác.")
            # Chuyển sang API Key tiếp theo
            current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
            api_key = get_current_api_key()

# Determine device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Tải mô hình và chuyển sang GPU (nếu có)
model = SentenceTransformer('dangvantuan/vietnamese-embedding', device = device)

def embedding_vietnamese(text):
    embedding = model.encode(text)
    return embedding



def preprocess_text_vietnamese(text):
    # Process text with spaCy pipeline
    doc = nlp(text)
    # Filter out stopwords and punctuation, and convert to lowercase
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    # Join tokens back into a single string
    processed_text = ' '.join(tokens)
    return processed_text, tokens

def calculate_similarity(query_features, reference_features):
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores

def compare_with_content(sentence, combined_webpage_text):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    sentences_from_webpage = split_sentences(combined_webpage_text)
    if sentences_from_webpage == []:
        return 0, "", -1
    sentences = remove_sentences(sentences_from_webpage)
    if sentences == []:
        return 0, "", -1
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]

    all_sentences = [preprocessed_query] + preprocessed_references
    print(len(all_sentences))
    if len(all_sentences) == 1319:
        print(combined_webpage_text)
    embeddings = embedding_vietnamese(all_sentences) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:]) 
    
    if similarity_scores.shape[1] == 0:
        return 0, ""
    
    max_similarity_idx = similarity_scores.argmax()
    max_similarity = similarity_scores[0][max_similarity_idx]
    best_match = sentences[max_similarity_idx]
    return max_similarity, best_match, max_similarity_idx

def compare_sentences(sentence, all_snippets):
    # Tiền xử lý câu và các snippet
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(snippet)[0] for snippet in all_snippets]  
    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = embedding_vietnamese(all_sentences) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:]) 
    # Sắp xếp điểm số tương đồng và chỉ số của các snippet
    sorted_indices = similarity_scores[0].argsort()[::-1]
    top_indices = sorted_indices[:3]
    top_scores = similarity_scores[0][top_indices]
    # Trả về ba điểm số độ tương đồng cao nhất và các chỉ số tương ứng
    top_similarities = [(top_scores[i], top_indices[i]) for i in range(len(top_indices))]
    
    return top_similarities

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
    # Phân tích HTML với BeautifulSoup
    # Sử dụng BeautifulSoup để phân tích cú pháp HTML
    soup = BeautifulSoup(html, 'html.parser')
    if soup.body:
        # Lấy tất cả nội dung hiển thị trên trang web từ thẻ <body>
        body_content = soup.body.get_text(separator='\n', strip=True)
    elif soup.html:  # Nếu không có <body>, thử lấy nội dung từ thẻ <html>
        body_content = soup.html.get_text(separator='\n', strip=True)
    else:
        # Nếu không có <body> hoặc <html>, trả về chuỗi rỗng hoặc thông báo lỗi
        body_content = ""

    return body_content

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
        
        # Kiểm tra Content-Type để xác định loại tệp
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type:
            return extract_text_from_pdf(url, 'downloaded_document.pdf')
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
            return fetch_docx(url) 
        elif 'text/csv' in content_type:
            return fetch_csv(url)  
        else:
            return extract_text_from_html(response.text) 
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error accessing {url}: {e}")
        return ""


# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
es = Elasticsearch("http://localhost:9200")

sentence_file = './test/Data/test_sentence.txt'
output_file = './test/Data/search.txt'

def search_sentence_elastic(sentence):
    # Xử lý từng câu và lấy danh sách tokens
    processed_sentence, tokens = preprocess_text_vietnamese(sentence)
    print(f"Processed sentence: {processed_sentence}")
    print(f"Tokens: {tokens}")
    # Tạo danh sách các field_value từ Elasticsearch
    sentence_results = []  # Mảng lưu trữ kết quả từng câu
    seen_ids = set()  # Tập lưu các mongo_id đã thấy
    if not tokens:
        return None, []
    res = es.search(index="plagiarism", body={
        "query": {
            "match": {"sentence": sentence}
        },
        "size": 10
    })
    
    for hit in res['hits']['hits']:
        mongo_id = hit['_source']['mongo_id']
        
        # Nếu mongo_id chưa thấy, mới thêm vào kết quả
        if mongo_id not in seen_ids:
            seen_ids.add(mongo_id)
            log_entry = hit['_source']['log_entry']
            log_entry = log_entry.replace("=>", ":").replace("BSON::ObjectId(", "").replace(")", "").replace("'", '"')
            
            # Phân tích chuỗi JSON
            data = json.loads(log_entry)
            
            # Truy cập các giá trị
            sentence = data.get("sentence")
            sentence_index = data.get("sentence_index")
            page_number = data.get("page_number")
            file_name = data.get("file_name")
            
            result_info = {
                'page_number': page_number,
                'sentence_index': sentence_index,
                'sentence_content': sentence,
                'file_name': file_name,
            }
            sentence_results.append(result_info)

    # Ghi kết quả vào file
    with open(output_file, 'w', encoding='utf-8') as file:
        sentence_contents = [] 
        for result in sentence_results:
            page_number = result['page_number']
            sentence_index = result['sentence_index']
            sentence_content = result['sentence_content']
            file_name = result['file_name']
            file.write(f"Sentence: {processed_sentence}, Elasticsearch result: File: {file_name}, Trang: {page_number}; Số câu: {sentence_index}; Nội dung: {sentence_content}\n")             
            sentence_contents.append(sentence_content)
    return processed_sentence, sentence_contents

def search_sentence_elastic_embedding(sentence): 
    processed_sentence, _ = preprocess_text_vietnamese(sentence)
    sentence_results = []  # Mảng lưu trữ kết quả từng câu

    res = es.search(index="plagiarism_embedding", body={"query": {"match": {"sentence": processed_sentence}}})
    for hit in res['hits']['hits']:
        log_entry = hit['_source']['log_entry']
        log_entry = log_entry.replace("=>", ":").replace("BSON::ObjectId(", "").replace(")", "").replace("'", '"')
        # Phân tích chuỗi JSON
        data = json.loads(log_entry)
        # Truy cập các giá trị
        sentence = data.get("sentence")
        sentence_index = data.get("sentence_index")
        page_number = data.get("page_number")
        embedding = data.get("Embedding")
        result_info = {
            'page_number': page_number,
            'sentence_index': sentence_index,
            'sentence_content': sentence,
            'embedding': embedding
        }
        sentence_results.append(result_info)  
    # Ghi kết quả vào file
    with open(output_file, 'w', encoding='utf-8') as file:
        embeddings = [] 
        sentence_contents = [] 
        for result in sentence_results:
            page_number = result['page_number']
            sentence_index = result['sentence_index']
            sentence_content = result['sentence_content']
            embedding = result['embedding']
            file.write(f"sentence: {sentence}, Elasticsearch result: Trang: {page_number}; Số câu: {sentence_index}; Nội dung: {sentence_content}\n")
            embeddings.append(embedding)              
            sentence_contents.append(sentence_content)
        file.write("\n")

    return processed_sentence, sentence_contents, embeddings


def calculate_dynamic_threshold(length, max_threshold=0.9, min_threshold=0.7):
    if length < 10:
        return max_threshold
    elif length > 40:
        return min_threshold
    else:
        scaling_factor = (max_threshold - min_threshold) / (40 - 10)
        threshold = max_threshold - (length - 10) * scaling_factor
        return threshold