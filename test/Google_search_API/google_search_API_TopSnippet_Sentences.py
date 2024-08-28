import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
from save_txt import *
from processing import *
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

sentences_cache = {}
plagiarized_count = 0

def search_text(text):
    global plagiarized_count
    sentences = text.split('\n')

    for i, sentence in enumerate(sentences):
        print(f"********Tìm kiếm câu {i + 1}: {sentence}")
        result = search_google(sentence)
        items = result.get('items', [])
        all_snippets = [item.get('snippet', '') for item in items if item.get('snippet', '')]
        if not all_snippets:
            continue 
        top_similarities  = compare_sentences(sentence, all_snippets)
        best_match_url = None
        best_match_title = None
        best_match_similarity = 0
        best_match_sentence = ""
        for _, idx in top_similarities:
            url = items[idx].get('link')
            title = items[idx].get('title')
            snippet = all_snippets[idx]
            print(f"Checking URL: {url}")
            # Tìm trong cache trước khi tải nội dung
            sentences = sentences_cache.get(url)
            
            if sentences is None:
                content = fetch_url(url)
                sentences_from_webpage = split_sentences(content)
                sentences = remove_sentences(sentences_from_webpage)
                sentences_cache[url] = sentences

            if sentences:             
                snippet_parts = split_snippet(snippet)
                # snippet_parts = remove_snippet_parts(snippet_parts)
                # Lọc các câu chứa ít nhất một phần của snippet
                relevant_sentences = [s for s in sentences if check_snippet_in_sentence(s, snippet_parts)]
                if relevant_sentences:
                    similarity_sentence, match_sentence, _ = compare_with_sentences(sentence, relevant_sentences)
                    if similarity_sentence > best_match_similarity:
                        best_match_similarity = similarity_sentence
                        best_match_url = url
                        best_match_title = title
                        best_match_sentence = match_sentence

        # Kiểm tra kết quả và cập nhật nếu phát hiện đạo văn
        if best_match_url:
            threshold = calculate_dynamic_threshold(len(sentence.split()))
            print(f"Độ tương đồng: {best_match_similarity}")
            print(f"Ngưỡng: {threshold}")
            if best_match_similarity > threshold:
                print("+++++++Nội dung bị trùng phát hiện:")
                print(f"Title: {best_match_title}")
                print(f"URL: {best_match_url}")
                print(f"Best match sentence: {best_match_sentence}")
                plagiarized_count += 1


with open('./test/Data/test_2.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# Start the timer
start_time = time.time()
search_text(text)
sentences_cache.clear()
end_time = time.time()
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của Google Search API ")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
