import requests
import spacy
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor
import os
from processing import *
from difflib import SequenceMatcher
import warnings
from urllib3.exceptions import InsecureRequestWarning
import certifi
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
    if url.endswith('.pdf'):
        save_path = 'downloaded_document.pdf'  # Đường dẫn lưu file PDF tạm thời
        return fetch_and_process_pdf(url, save_path)
    else:
        try:
            response = requests.get(url, verify= False)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None    
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

def similar(a, b):
    # Tiền xử lý văn bản
    processed_a, _ = preprocess_text_vietnamese(a)
    processed_b, _ = preprocess_text_vietnamese(b)
    return SequenceMatcher(None, processed_a, processed_b).ratio()

def compare_with_webpage(sentence, webpage_text):
    max_similarity = 0
    best_match = ""
    
    # Tiền xử lý câu cần so sánh
    processed_sentence, _ = preprocess_text_vietnamese(sentence)
    
    # Chia nội dung trang web thành các đoạn nhỏ hơn nếu cần
    for i in range(0, len(webpage_text), nlp.max_length):
        doc = nlp(webpage_text[i:i + nlp.max_length])
        for sent in doc.sents:
            web_sentence = sent.text
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
        for item in items:
            url = item.get('link')
            print(url)
            content = fetch_webpage_or_pdf(url)
            if url.endswith('.pdf'):
                webpage_text = content
            else:
                webpage_text = extract_text_from_html(content)
            max_similarity, best_match = compare_with_webpage(sentence, webpage_text)
            print(f"Title: {item.get('title')}")
            print(f"URL: {url}")
            print(f"Best match sentence: {best_match}")
            print(f"Similarity: {max_similarity}\n")
            
            # Kiểm tra nếu mức độ tương đồng lớn hơn ngưỡng nhất định (ví dụ 0.5)
            if max_similarity > 0.5:
                print("+++++++Nội dung bị trùng phát hiện:")
                print(f"Best match sentence: {best_match}\n")
with open('./test/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# Văn bản cần kiểm tra đạo văn
search_text(text)