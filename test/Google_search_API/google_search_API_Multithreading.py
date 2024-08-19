import concurrent.futures
import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time

# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Dictionary để lưu trữ nội dung các file PDF và nội dung trang web
content_cache = {}
plagiarized_count = 0

def fetch_and_cache_url(url):
    """Lấy nội dung từ URL và lưu vào cache."""
    if url not in content_cache:
        content_cache[url] = fetch_url(url)
    return content_cache[url]

def process_sentence(sentence):
    global plagiarized_count
    print(f"********Tìm kiếm câu: {sentence}")
    result = search_google(sentence)
    items = result.get('items', [])
    all_snippets = [item.get('snippet', '') for item in items if item.get('snippet', '')]
    if not all_snippets:
        return

    top_similarities  = compare_sentences(sentence, all_snippets)
    best_match_url = None
    best_match_title = None
    best_match_similarity = 0
    best_match_sentence = ""
    for similarity, idx in top_similarities:
        url = items[idx].get('link')
        title = items[idx].get('title')
        print(f"Checking URL: {url}")
        content = None
        if url in content_cache:
            content =  content_cache[url]
        else:
            content = fetch_url(url)
            content_cache[url] = content
        if content:
            similarity, match_sentence, _ = compare_with_content(sentence, content)        
            if similarity > best_match_similarity:
                best_match_similarity = similarity
                best_match_url = url
                best_match_title = title
                best_match_sentence = match_sentence

    # In ra thông tin của URL, tiêu đề và câu trùng khớp có độ tương đồng cao nhất
    if best_match_url:
        print(f"Max Similarity: {best_match_similarity}")
        threshold = calculate_dynamic_threshold(len(sentence.split()))
        print(f"Threshold: {threshold}")
        if best_match_similarity > threshold:
            print("+++++++Nội dung bị trùng phát hiện:")
            print(f"Title: {best_match_title}")
            print(f"URL: {best_match_url}")
            print(f"Best match sentence: {best_match_sentence}")
            plagiarized_count += 1

def search_text(text):
    sentences = text.split('\n')

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_sentence, sentence) for sentence in sentences]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

with open('./test/Data/test_2.txt', 'r', encoding='utf-8') as file:
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
