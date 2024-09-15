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

import difflib


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
    'AIzaSyATVTCw6KpsRrTpot-B8M5ON0J06uULkD4',
    'AIzaSyBpjtdhFaONvHjaf-YLZqSBMwigv5OetnA',
    'AIzaSyBLwEhO1xq-p57LR5NjccC0ym2_ZdV-oSI',
    'AIzaSyBwIrGwgFYQI47PrY3VTnvrEuUC4Ei5V_Q',
    'AIzaSyB4dVUMkfQE5fd5-ehopPC6XM3pl0oQerk',
    'AIzaSyAF73pow1YLtPLsyxT7mnGd0eB4nMdzRJU',

]
CX = 'f5a8b4e14ca474f61'

API_KEYS2 = [
    'AIzaSyDBhQBb0pKBPTh1iiLikdtecc7PW9XaGFY',
    'AIzaSyBjbKPbW6nLb6lj9_a1inSitoSKkH0wo7o',
    'AIzaSyC35aTxM9bZpW4XFLiN0cZvMgLG83eKJRs',
    'AIzaSyAokaQBIB3uaUxAm9mZjpktV5YzaP8gYLI',
    'AIzaSyAh4EtsRgwRZLdgN3W2mTqfPj6AV2qdWwI',
    'AIzaSyBXv3I1N6DqClEJwZqZJpNT15272slb5uw',
    'AIzaSyCTcoSHq5-y1PYhePN9plTp3p27b1NKVWA',
    'AIzaSyD5lIcE4onfdWFcigcGfXMAP6UM0Zuk2Uk',
    'AIzaSyDAcREUVSuy4sfKs2Lh4OxuBvgF_rV9SqI',
    'AIzaSyBHOKyYLiSWETnNH0-e8ikQWmeN0BKi7BU',
    'AIzaSyBWx3xGBXLHO-XWys5LxIlOHodjDrU6lGA',
    'AIzaSyBt43IZ77nq8BwvLpaMDUTEFAfBGdlPqoo',
    
]

CX2 = 'a6694d6bf858e42f6'

API_KEYS3 = [
    'AIzaSyB9pd6wJ5oEO4-AN5F0kjtMKXH69ky3oe8',
    'AIzaSyBhEFWEralUvFNsuqjrwZhMX__YjbBIDeo',
    'AIzaSyC5965PVE6g5mhSL_nSZoDcxFihduk3Vok',
    'AIzaSyCKAEdJwGwhiJxA8bGXm_lbi3ZHnSRGCGc',
    'AIzaSyDEKcMT2Sn0xNJGLFhXt6X4d9t0D5onw5A',
    'AIzaSyD_z3VYwanzMQcrCiRan-5jplIhAJKLnoM',
    'AIzaSyB4odGdiBhlrZcrOrngwcHIM_FlLweCX80',
    'AIzaSyBPRxRJWlr8q4v81xGMshDyJKpc_dGWODg',
    'AIzaSyALCy-7PoY_SZ425b3V4IBMnTLcrm2QFmg',
    'AIzaSyDQq2ppxwmYWtW8aGQUi9RTh1g7tpk6KOc',
    'AIzaSyBmBPKHZAXMd35HjNDCEMMeSpqgp4CDcBo',
    'AIzaSyB-dx-CFUpzfsGagGT9-4wiYAhc4PsIyD0',
]
CX3 = 'c0c0ab4e2da9b4ef2'

API_KEYS4 = [
    'AIzaSyB3xLylKi869uTqRwOeZBMXPaHFOE4_WG0',
    'AIzaSyApQdG_sSdiG6zkUDzagXipLQFKM2O8mww',
    'AIzaSyDbSYjRWLeAHgDXohIORPxL4TG3wEMEnt0',
    'AIzaSyDFQcrxtpCvA3u98RuqYsdNhqOehX8VIe4',
    'AIzaSyAwECCGT_p6wOWz3cIUNJptiN0dnPRv8hs',
    'AIzaSyBwwA43nAbL_rNJrVs0Tx85elMrOg3Sm-U',
    'AIzaSyBqHNzB_YT8GwQML1x-eAcDXh3Kl9y1FDo',
    'AIzaSyArm92_Il9cFufWYN6zHnFwgjPodhvALHY',
    'AIzaSyCiRnAnm-RvoczOfcJ_Jp_uYEHjP8X5irQ',
    'AIzaSyBAoedWrVtHO-0iVuZKqzUwwpzMDlppqhE',
    'AIzaSyD0jh0n0mEsd_acUt7yTuLasXeHQk6auGU',
    'AIzaSyAe4kQFGeVqXnD0-EIx5qAUxA4aeauTx_Y',
]
CX4 = '01d819c8b90df4a04'


# Khởi tạo API Key hiện tại
# Biến toàn cục
current_api_key_index = 0
current_list = 1  

def get_current_api_key():
    """Trả về API Key hiện tại."""
    global current_list
    if current_list == 1 and current_api_key_index < len(API_KEYS):
        return API_KEYS[current_api_key_index]
    elif current_list == 2 and current_api_key_index < len(API_KEYS2):
        return API_KEYS2[current_api_key_index]
    elif current_list == 3 and current_api_key_index < len(API_KEYS3):
        return API_KEYS3[current_api_key_index]
    elif current_list == 4 and current_api_key_index < len(API_KEYS4):
        return API_KEYS4[current_api_key_index]
    return None

def get_next_api_key():
    """Chuyển sang API Key tiếp theo, và chuyển danh sách khi hết key."""
    global current_api_key_index, current_list
    current_api_key_index += 1

    # Kiểm tra nếu danh sách hiện tại hết API Key
    if current_list == 1 and current_api_key_index >= len(API_KEYS):
        # Chuyển sang danh sách API_KEYS2
        current_list = 2
        current_api_key_index = 0  # Reset lại index cho API_KEYS2
    elif current_list == 2 and current_api_key_index >= len(API_KEYS2):
        # Chuyển sang danh sách API_KEYS2
        current_list = 3
        current_api_key_index = 0  # Reset lại index cho API_KEYS2
    elif current_list == 3 and current_api_key_index >= len(API_KEYS3):
        # Chuyển sang danh sách API_KEYS2
        current_list = 4
        current_api_key_index = 0  # Reset lại index cho API_KEYS2
    elif current_list == 4 and current_api_key_index >= len(API_KEYS4):
        return None  # Đã dùng hết cả hai danh sách

    return get_current_api_key()

def search_google(query):
    """Tìm kiếm Google với các API Key, chuyển sang key tiếp theo khi gặp lỗi 403 hoặc 429."""
    global current_api_key_index, current_list
    while True:
        api_key = get_current_api_key()
        
        if api_key is None:
            print("Đã hết tất cả API Key.")
            return {}  # Trả về rỗng khi không còn API Key khả dụng
        
        # Chọn CX tương ứng với danh sách API
        if current_list == 1:
            cx = CX
        elif current_list == 2:
            cx = CX2
        else:
            cx = CX3
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
        response = requests.get(url, verify=False)
        
        if response.status_code == 200:
            return response.json()  # Trả về dữ liệu khi thành công
        
        elif response.status_code in [403, 429]:
            print(f"API Key {api_key} gặp lỗi {response.status_code}. Chuyển sang key khác.")
            api_key = get_next_api_key()  # Chuyển sang API Key tiếp theo
            
            if api_key is None:
                print("Không còn API Key nào khả dụng.")
                return {}  # Trả về rỗng nếu không còn API Key
            
        else:
            print(f"Yêu cầu không thành công với API Key {api_key}. Mã lỗi: {response.status_code}")
            return {}
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

def compare_with_content(sentence, content):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    sentences_from_webpage = split_sentences(content)
    if sentences_from_webpage == None:
        return 0, "", -1
    sentences = remove_sentences(sentences_from_webpage)
    if sentences == None:
        return 0, "", -1
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]

    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = embedding_vietnamese(all_sentences) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:]) 
    
    if similarity_scores.shape[1] == 0:
        return 0, "", -1
    
    max_similarity_idx = similarity_scores.argmax()
    max_similarity = similarity_scores[0][max_similarity_idx]
    best_match = sentences[max_similarity_idx]
    return max_similarity, best_match, max_similarity_idx

def compare_with_sentences(sentence, sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]

    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = embedding_vietnamese(all_sentences) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:]) 
    
    if similarity_scores.shape[1] == 0:
        return 0, "", -1
    
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
    top_indices = sorted_indices[:10]
    top_scores = similarity_scores[0][top_indices]
    # Trả về ba điểm số độ tương đồng cao nhất và các chỉ số tương ứng
    top_similarities = [(top_scores[i], top_indices[i]) for i in range(len(top_indices))]
    return top_similarities

def check_snippet_in_sentence(sentence, snippet_parts):
    # Kiểm tra xem câu có chứa bất kỳ phần nào của snippet hay không
    return any(part in sentence for part in snippet_parts)

def fetch_response(url):
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return response
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error accessing {url}: {e}")
        return None

def extract_text_from_pdf(response):
    try:
        pdf_source = io.BytesIO(response.content)  # Sử dụng .content để lấy dữ liệu dạng bytes
        with fitz.open(stream=pdf_source, filetype='pdf') as document:
            # Sử dụng ThreadPoolExecutor để xử lý đồng thời các trang
            with ThreadPoolExecutor() as executor:
                text_parts = executor.map(lambda page: page.get_text("text"), document)
            pdf_text = ''.join(text_parts)
    except Exception as e:
        print(f"Lỗi khi xử lý PDF: {e}")
        return ""
    return pdf_text

def extract_text_from_html(response):
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.body:
            # Lấy tất cả nội dung hiển thị trên trang web từ thẻ <body>
            body_content = soup.body.get_text(separator='\n', strip=True)
        elif soup.html:  # Nếu không có <body>, thử lấy nội dung từ thẻ <html>
            body_content = soup.html.get_text(separator='\n', strip=True)
        else:
            # Nếu không có <body> hoặc <html>, trả về chuỗi rỗng hoặc thông báo lỗi
            body_content = ""
        return body_content
    except Exception as e:
        print(f"Lỗi khi xử lý HTML: {e}")
        return ""

def fetch_docx(response):
    try:
        doc_file = BytesIO(response.content)
        doc = Document(doc_file)
        return '\n'.join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"Lỗi khi xử lý DOCX: {e}")
        return ""

def fetch_csv(response):
    try:
        csv_content = StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_content)
        return df.to_string()  # Trả về dữ liệu CSV dưới dạng chuỗi
    except Exception as e:
        print(f"Lỗi khi xử lý CSV: {e}")
        return ""

def fetch_url(url):
    response = fetch_response(url)
    if not response:
        return ""
    
    content_type = response.headers.get('Content-Type', '').lower()

    if 'application/pdf' in content_type:
        return extract_text_from_pdf(response)
    elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
        return fetch_docx(response)
    elif 'text/csv' in content_type:
        return fetch_csv(response)
    else:
        return extract_text_from_html(response)


# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
es = Elasticsearch("http://localhost:9200")

output_file = './test/Data/search.txt'

def search_sentence_elastic(sentence):
    # Xử lý từng câu và lấy danh sách tokens
    processed_sentence, tokens = preprocess_text_vietnamese(sentence)
    print(f"Processed sentence: {processed_sentence}")
    print(f"Tokens: {tokens}")
    # Tạo danh sách các field_value từ Elasticsearch
    sentence_results = []  # Mảng lưu trữ kết quả từng câu
    if not tokens:
        return None, []
    res = es.search(index="plagiarism", body={
        "query": {
            "match": {"sentence": sentence}
        },
        "size": 10
    })
    for hit in res['hits']['hits']:
        school_id = hit['_source']['school_id']
        school_name = hit['_source']['school_name']
        file_id = hit['_source']['file_id']
        file_name = hit['_source']['file_name']
        num_of_sentence = hit['_source']['num_of_sentence']
        sentence = hit['_source']['sentence']

        result_info = {
            'school_id': school_id,
            'school_name': school_name,
            'file_id': file_id,
            'file_name': file_name,
            'num_of_sentence': num_of_sentence,
            'sentence': sentence
        }
        sentence_results.append(result_info)
    return processed_sentence, sentence_results


def calculate_dynamic_threshold(length, max_threshold=0.8, min_threshold=0.5):
    if length < 10:
        return max_threshold
    elif length > 40:
        return min_threshold
    else:
        scaling_factor = (max_threshold - min_threshold) / (40 - 10)
        threshold = max_threshold - (length - 10) * scaling_factor
        return threshold
    

# Highlight

def read_pdf_binary(file_path):
    with open(file_path, 'rb') as file:
        return file.read()
    
def common_ordered_words_difflib(best_match, sentence):
    # Loại bỏ ký tự đặc biệt, chỉ giữ lại chữ cái và chữ số
    def clean_text(text):
        # Thay thế các ký tự không phải chữ cái, chữ số và khoảng trắng bằng chuỗi rỗng
        return re.sub(r'[^\w\s]', '', text).lower().split()

    # Chuyển về chữ thường và tách từ sau khi làm sạch
    words_best_match = clean_text(best_match)
    words_sentence = clean_text(sentence)

    seq_matcher = difflib.SequenceMatcher(None, words_best_match, words_sentence)
    
    common_words = []
    indices_best_match = []
    indices_sentence = []
    
    for match in seq_matcher.get_matching_blocks():
        if match.size > 0:  # Nếu có từ giống nhau
            common_words.extend(words_best_match[match.a: match.a + match.size])
            indices_best_match.extend(range(match.a, match.a + match.size))
            indices_sentence.extend(range(match.b, match.b + match.size))

    return len(common_words), indices_best_match, indices_sentence
