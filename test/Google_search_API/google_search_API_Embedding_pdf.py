import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
from save_txt import *
from processing import *

# Thêm đường dẫn của thư mục cha vào sys.path

# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Bắt đầu tính thời gian
start_time = time.time()
file_path = './Data/SKL007296.pdf'

# Dictionary để lưu trữ nội dung các file PDF và nội dung trang web
content_cache = {}
plagiarized_count = 0
processed_sentences = []

def processing_data(file_path):
    # Trích xuất nội dung văn bản từ file PDF với số trang
    text_with_page = extract_pdf_text(file_path)
    # Lưu nội dung vào file văn bản với số trang
    save_text_with_page_to_file(text_with_page, './output/content.txt')
    # Kết hợp các dòng và tách câu, lưu cả số trang cho mỗi câu
    sentences_with_page = combine_lines_and_split_sentences(text_with_page)
    # Lưu nội dung vào file văn bản với số dòng và số trang
    save_combined_text_with_page_to_file(sentences_with_page, './output/sentence_split.txt')
    # Loại bỏ các câu có ít hơn 1 từ
    processed_sentences = remove_single_word_sentences(sentences_with_page)
    # Lưu nội dung vào file văn bản
    save_combined_text_with_page_to_file(processed_sentences, './output/processed_sentences.txt')
    return processed_sentences

def handle_sentence(sentence_data):
    global plagiarized_count

    sentence, _ = sentence_data
    print(f"********Tìm kiếm câu: {sentence}")
    
    result = search_google(sentence)
    items = result.get('items', [])
    all_snippets = [item.get('snippet', '') for item in items if item.get('snippet', '')]
    
    if not all_snippets:
        return None

    top_similarities = compare_sentences(sentence, all_snippets)
    best_match_url = None
    best_match_title = None
    best_match_similarity = 0
    best_match_sentence = ""

    for _, idx in top_similarities:
        url = items[idx].get('link')
        title = items[idx].get('title')
        print(f"Checking URL: {url}")
        
        # Tìm trong cache trước khi tải nội dung
        content = content_cache.get(url)
        
        if content is None:
            content = fetch_url(url)
            content_cache[url] = content
        
        if content:
            similarity_sentence, match_sentence, _ = compare_with_content(sentence, content)
            
            if similarity_sentence > best_match_similarity:
                best_match_similarity = similarity_sentence
                best_match_url = url
                best_match_title = title
                best_match_sentence = match_sentence

    # Kiểm tra kết quả và cập nhật nếu phát hiện đạo văn
    if best_match_url:
        threshold = calculate_dynamic_threshold(len(sentence.split()))
        print(f"Độ tương đồng: {best_match_similarity}")
        print(f"Ngưỡng:{threshold}")
        if best_match_similarity > threshold:
            print("+++++++Nội dung bị trùng phát hiện:")
            print(f"Title: {best_match_title}")
            print(f"URL: {best_match_url}")
            print(f"Best match sentence: {best_match_sentence}")
            plagiarized_count += 1

    return best_match_url

# Tiền xử lý dữ liệu từ file PDF
processed_sentences = processing_data(file_path)

# Xử lý từng câu lần lượt (đơn luồng)
for i, sentence_data in enumerate(processed_sentences):
    print(f"Câu {i+1}")
    handle_sentence(sentence_data)

# Dọn dẹp cache
content_cache.clear()

# Kết thúc và in ra thời gian thực hiện
end_time = time.time()
elapsed_time = end_time - start_time

print("Đánh giá độ hiệu quả của Google Search API ")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
