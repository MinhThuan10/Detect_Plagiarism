import requests
import spacy
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor
import os
import io
from processing import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import re
import time

# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
# Tải mô hình ngôn ngữ
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")
# Tăng giới hạn max_length
nlp.max_length = 2000000
API_KEY = 'AIzaSyBf9wrYHM4SYW9w-jvA-PIIF-VJKI4owaA'
CX = 'f5a8b4e14ca474f61'

# Dictionary để lưu trữ nội dung các file PDF và nội dung trang web
content_cache = {}

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    response = requests.get(url, verify=False)
    return response.json()

def extract_text_from_pdf(url, save_path):
    # Tải PDF từ URL
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        return ""

    # Lưu tạm thời file PDF nếu cần
    if save_path:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        pdf_path = save_path
    else:
        pdf_path = io.BytesIO(response.content)

    # Trích xuất văn bản từ PDF
    with fitz.open(pdf_path) as document:
        with ThreadPoolExecutor() as executor:
            text_parts = executor.map(lambda page: page.get_text("text"), document)
    
    pdf_text = ''.join(text_parts)

    # Lưu nội dung vào cache và xóa file tạm nếu cần
    content_cache[url] = pdf_text
    if save_path:
        os.remove(save_path)
    
    return pdf_text

def fetch_webpage_or_pdf(url):
    if url in content_cache:
        return content_cache[url]
    
    try:
        response = requests.get(url, timeout=10, verify=False)  # Thêm timeout 10 giây
        response.raise_for_status()
        if url.endswith('.pdf'):
            return extract_text_from_pdf(url, 'downloaded_document.pdf')
        else:
            html_content = response.text
            webpage_text = extract_text_from_html(html_content)
            # Lưu nội dung vào cache
            content_cache[url] = webpage_text
            return webpage_text
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error accessing {url}: {e}")
        return ""

def extract_text_from_html(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    for script in soup(["script", "style"]):
        script.extract()  # Remove script and style tags
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def calculate_similarity(query_features, reference_features):
    # Check dimensions and transpose if necessary
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    
    # Check dimensions again after potential transposition
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores

def similar(a, b):
    # Tính toán TF-IDF cho hai câu
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([a, b])
    # Xác định số lượng đặc trưng (features)
    n_features = features.shape[1]
    # Xác định số lượng thành phần SVD (không vượt quá số lượng đặc trưng)
    n_components = min(100, n_features)
    # Áp dụng TruncatedSVD để thực hiện LSA
    svd = TruncatedSVD(n_components=n_components)
    features_lsa = svd.fit_transform(features)
    # Tách riêng các vector đặc trưng của hai câu
    features_a_lsa = features_lsa[0].reshape(1, -1)
    features_b_lsa = features_lsa[1].reshape(1, -1)
    # Tính độ tương đồng cosine
    similarity_score = calculate_similarity(features_a_lsa, features_b_lsa)[0][0]
    return similarity_score

def combine_lines_and_split_sentences(text):
    combined_sentences = []
    # Bao gồm tất cả các ký tự thường trong tiếng Việt
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    
    # Thay thế '\n' theo điều kiện: Nếu có ký tự '\n' và sau đó là chữ thường tiếng Việt
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

def compare_with_webpage(sentence, webpage_text):
    max_similarity = 0
    best_match = ""
    
    # Tiền xử lý câu cần so sánh
    processed_sentence, _ = preprocess_text_vietnamese(sentence)
    
    # Tách câu từ văn bản trang web
    sentences_from_webpage = combine_lines_and_split_sentences(webpage_text)
    
    for web_sentence in sentences_from_webpage:
        # Tiền xử lý câu từ trang web
        processed_web_sentence, _ = preprocess_text_vietnamese(web_sentence)
        similarity = similar(processed_sentence, processed_web_sentence)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = web_sentence
    return max_similarity, best_match

def calculate_dynamic_threshold(length, max_threshold=0.85, min_threshold=0.65):
    """
    Tính toán ngưỡng phát hiện đạo văn động dựa trên chiều dài câu.
    """
    # Xác định tỷ lệ thay đổi ngưỡng dựa trên chiều dài câu
    if length < 15:
        return max_threshold  # Đối với câu rất ngắn, sử dụng ngưỡng tối đa
    elif length > 45:
        return min_threshold  # Đối với câu dài, sử dụng ngưỡng tối thiểu
    else:
        # Tính toán ngưỡng cho chiều dài câu trong phạm vi từ 15 đến 45
        scaling_factor = (max_threshold - min_threshold) / (45 - 15)
        threshold = max_threshold - (length - 15) * scaling_factor
        return threshold

plagiarized_count = 0
def search_text(text):
    global plagiarized_count
    sentences = text.split('\n')
    i = 0
    
    for sentence in sentences:
        i += 1
        print(f"********Tìm kiếm câu {i}: {sentence}")
        result = search_google(sentence)
        items = result.get('items', [])
        max_similarity = 0
        best_match_sentence = ""
        best_match_url = ""
        best_match_title = ""

        for item in items:
            url = item.get('link')
            print(f"Checking URL: {url}")
            content = fetch_webpage_or_pdf(url)
            similarity, match_sentence = compare_with_webpage(sentence, content)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_sentence = match_sentence
                best_match_url = url
                best_match_title = item.get('title', '')
        print(f"Similarity: {max_similarity}")        
        # Tính ngưỡng động dựa trên chiều dài câu
        query_length = len(sentence.split())
        dynamic_threshold = calculate_dynamic_threshold(query_length)
        if max_similarity > dynamic_threshold:
            plagiarized_count += 1
            print(f"Plagiarized content found:\nSentence: {sentence}\nBest match: {best_match_sentence}\nURL: {best_match_url}\nTitle: {best_match_title}\nSimilarity: {max_similarity}")

with open('./test/test_2.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# Start the timer
start_time = time.time()
search_text(text)
content_cache.clear()
end_time = time.time()
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của Google Search API ")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
