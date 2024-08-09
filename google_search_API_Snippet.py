import requests
from PyPDF2 import PdfReader
import warnings
from urllib3.exceptions import InsecureRequestWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import re
import time
from bs4 import BeautifulSoup
import spacy
from processing import preprocess_text_vietnamese
from io import BytesIO
import fitz  # PyMuPDF

start_time = time.time()

# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Tải mô hình ngôn ngữ
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")

# Tăng giới hạn max_length
nlp.max_length = 2000000

API_KEY = 'AIzaSyBf9wrYHM4SYW9w-jvA-PIIF-VJKI4owaA'
CX = 'f5a8b4e14ca474f61'

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    response = requests.get(url, verify=False)
    return response.json()

def calculate_similarity(query_features, reference_features):
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores

def similar(a, b):
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([a, b])
    n_features = features.shape[1]
    n_components = min(100, n_features)
    svd = TruncatedSVD(n_components=n_components)
    features_lsa = svd.fit_transform(features)
    features_a_lsa = features_lsa[0].reshape(1, -1)
    features_b_lsa = features_lsa[1].reshape(1, -1)
    similarity_score = calculate_similarity(features_a_lsa, features_b_lsa)[0][0]
    return similarity_score

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

def compare_with_webpage(sentence, relevant_texts):
    max_similarity = 0
    best_match = ""
    
    processed_sentence, _ = preprocess_text_vietnamese(sentence)
    for text in relevant_texts:
        sentences_from_webpage = combine_lines_and_split_sentences(text)
        for web_sentence in sentences_from_webpage:
            processed_web_sentence, _ = preprocess_text_vietnamese(web_sentence)
            similarity = similar(processed_sentence, processed_web_sentence)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = web_sentence
    return max_similarity, best_match

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
                similarity, match_sentence = compare_with_webpage(sentence, [snippet])
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_sentence = match_sentence
                    best_match_url = item.get('link')
                    best_match_title = item.get('title')
        if best_match_sentence:
            print(f"Max Similarity: {max_similarity}\n")
            query_length = len(sentence.split())
            dynamic_threshold = calculate_dynamic_threshold(query_length)
            
            if max_similarity > dynamic_threshold:
                plagiarized_count += 1
                print("+++++++Nội dung bị trùng phát hiện:")
                print(f"Title: {best_match_title}")
                print(f"URL: {best_match_url}")
                print(f"Best match sentence: {best_match_sentence}")
                print(f"Max Similarity: {max_similarity}\n")

with open('./test/test_2.txt', 'r', encoding='utf-8') as file:
    text = file.read()

search_text(text)

end_time = time.time()
elapsed_time = end_time - start_time
print("Đánh giá hiệu quả của Google Search API:")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
