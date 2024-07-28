import requests
import spacy
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor
import os
from processing import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import re

# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
# Tải mô hình ngôn ngữ
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")
# Tăng giới hạn max_length
nlp.max_length = 2000000

API_KEY = 'AIzaSyDS7CJVx66LdxmC9RlIhoQKsiDz6Vbb40k'
CX = 'f5a8b4e14ca474f61'

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    response = requests.get(url, verify= False)
    return response.json()

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    num_pages = document.page_count

    def extract_page_text(page_num):
        page = document.load_page(page_num)
        return page.get_text("text")

    with ThreadPoolExecutor() as executor:
        text_parts = list(executor.map(extract_page_text, range(num_pages)))

    return ''.join(text_parts)

def fetch_and_process_pdf(url, save_path):
    response = requests.get(url, verify= False)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        
        # Trích xuất nội dung từ file PDF đã lưu
        pdf_text = extract_text_from_pdf(save_path)
        
        # Xóa file PDF sau khi xử lý xong
        os.remove(save_path)
        
        return pdf_text
    return ""

def fetch_webpage_or_pdf(url):
    try:
        response = requests.get(url, timeout=60, verify=False)  # Thêm timeout 60 giây
        response.raise_for_status()
        if url.endswith('.pdf'):
            return fetch_and_process_pdf(url, 'downloaded_document.pdf')
        else:
            return response.text
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
    # print("Query features shape:", query_features.shape)
    # print("Reference features shape:", reference_features.shape)
    
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


def search_text(text):
    doc = nlp(text)
    for sent in doc.sents:
        sentence = sent.text
        print(f"**************************************************Tìm kiếm câu: {sentence}")
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
            if url.endswith('.pdf'):
                webpage_text = content
            else:
                webpage_text = extract_text_from_html(content)   

            similarity, match_sentence = compare_with_webpage(sentence, webpage_text)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_sentence = match_sentence
                best_match_url = url
                best_match_title = item.get('title')
                
        if best_match_sentence:
            print(f"++++++++++++++Best match for sentence: {sentence}")
            print(f"Title: {best_match_title}")
            print(f"URL: {best_match_url}")
            print(f"Best match sentence: {best_match_sentence}")
            print(f"Max Similarity: {max_similarity}\n")
            
            if max_similarity > 0.5:
                print("+++++++Nội dung bị trùng phát hiện:")
                print(f"Best match sentence: {best_match_sentence}\n")
with open('./test/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# Văn bản cần kiểm tra đạo văn
search_text(text)