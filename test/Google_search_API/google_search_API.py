from processing import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time

# Start the timer
start_time = time.time()
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

plagiarized_count = 0

def search_text(text):
    global plagiarized_count
    sentences = text.split('\n')
        
    for i, sentence in enumerate(sentences):
        print(f"********Tìm kiếm câu {i + 1}: {sentence}")
        result = search_google(sentence)
        items = result.get('items', [])
        
        best_match_url = None
        best_match_title = None
        best_match_similarity = 0
        best_match_sentence = ""

        for item in items:
            url = item.get('link')
            title = item.get('title')
            print(f"Checking URL: {url}")
            content = None
            content = fetch_url(url)
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


with open('./test/test_2.txt', 'r', encoding='utf-8') as file:
    text = file.read()

search_text(text)

# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của Google Search API ")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
