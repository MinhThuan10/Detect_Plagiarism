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
import time
from bs4 import BeautifulSoup
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Tải mô hình ngôn ngữ
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

def split_snippet(snippet):
    # Chia snippet thành các phần nhỏ hơn theo dấu chấm và loại bỏ dấu ba chấm
    parts = re.split(r'\.\.\.|(?<=\.)\s+', snippet)
    return [part.strip() for part in parts if part.strip()]


def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    for script in soup(["script", "style"]):
        script.extract()  # Remove script and style tags
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

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
    response = requests.get(url, verify=False)
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
        response = requests.get(url, timeout=10, verify=False)  # Thêm timeout 10 giây
        response.raise_for_status()
        if url.endswith('.pdf'):
            return fetch_and_process_pdf(url, 'downloaded_document.pdf')
        else:
            return response.text
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error accessing {url}: {e}")
        return ""

def compare_with_webpage(sentence, snippet_parts, webpage_text):
    max_similarity = 0
    best_match = ""

    # Tiền xử lý câu cần so sánh
    processed_sentence, _ = preprocess_text_vietnamese(sentence)
    
    # Tách câu từ văn bản trang web
    sentences_from_webpage = combine_lines_and_split_sentences(webpage_text)
    
    for web_sentence in sentences_from_webpage:
        # Kiểm tra xem câu từ trang web có chứa phần nào của snippet không
        if any(part in web_sentence for part in snippet_parts):
            # Tiền xử lý câu từ trang web
            processed_web_sentence, _ = preprocess_text_vietnamese(web_sentence)
            # So sánh câu
            similarity = similar(processed_sentence, processed_web_sentence)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = web_sentence
    
    return max_similarity, best_match


def similar(a, b):
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([a, b])
    n_features = features.shape[1]
    n_components = min(100, n_features)
    svd = TruncatedSVD(n_components=n_components)
    features_lsa = svd.fit_transform(features)
    features_a_lsa = features_lsa[0].reshape(1, -1)
    features_b_lsa = features_lsa[1].reshape(1, -1)
    similarity_score = cosine_similarity(features_a_lsa, features_b_lsa)[0][0]
    return similarity_score

def calculate_dynamic_threshold(length, max_threshold=0.85, min_threshold=0.65):
    if length < 15:
        return max_threshold
    elif length > 45:
        return min_threshold
    else:
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
            snippet = item.get('snippet', '')  # Lấy Featured Snippet
            if snippet:
                print(f"Snippet: {snippet}")
                snippet_parts = split_snippet(snippet)
                url = item.get('link')
                print(f"Checking URL: {url}")
                content = fetch_webpage_or_pdf(url)
                if url.endswith('.pdf'):
                    webpage_text = content
                else:
                    webpage_text = extract_text_from_html(content)

                similarity, match_sentence = compare_with_webpage(sentence, snippet_parts, webpage_text)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_sentence = match_sentence
                    best_match_url = url
                    best_match_title = item.get('title')

        if best_match_sentence:
            print(f"++++++++++++++Best match for sentence: {sentence}")
            print(f"Max Similarity: {max_similarity}\n")
            
            query_length = len(sentence.split())
            dynamic_threshold = calculate_dynamic_threshold(query_length)
            print(f"Threshold: {dynamic_threshold}\n")
            if max_similarity > dynamic_threshold:
                plagiarized_count += 1
                print("+++++++Nội dung bị trùng phát hiện:")
                print(f"Title: {best_match_title}")
                print(f"URL: {best_match_url}")
                print(f"Best match sentence: {best_match_sentence}")
                print(f"Max Similarity: {max_similarity}\n")

with open('./test/test_2.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# Start the timer
start_time = time.time()
search_text(text)

end_time = time.time()
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của Google Search API ")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
