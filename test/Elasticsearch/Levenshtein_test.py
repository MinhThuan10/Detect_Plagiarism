import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from processing_input import *
import Levenshtein as lev
import time

# Start the timer
start_time = time.time()

# Hàm tính tỷ lệ Levenshtein distance
def levenshtein_ratio_and_distance(s, t, ratio_calc=True):
    # Tính khoảng cách Levenshtein
    distance = lev.distance(s, t)
    if ratio_calc:
        # Tính tỷ lệ khoảng cách Levenshtein
        ratio = distance / max(len(s), len(t))
        return ratio
    else:
        return distance

plagiarized_count = 0

with open('./test/Data/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
    # Tách thành các câu và xử lý
sentences = text.split('\n')

for i, sentence in enumerate(sentences):
    preprocessed_query, all_sentences = search_sentence_elastic(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentences]   
   
    # Tính tỷ lệ Levenshtein distance giữa câu query và các câu tham chiếu
    levenshtein_scores = [levenshtein_ratio_and_distance(preprocessed_query, ref) for ref in preprocessed_references]
    # Tính ngưỡng động dựa trên chiều dài câu
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)

    # Tìm giá trị nhỏ nhất trong danh sách
    lowest_ratio = min(levenshtein_scores)

    # Tìm chỉ số của giá trị nhỏ nhất
    min_ratio_idx = levenshtein_scores.index(lowest_ratio)

    print(f"Score: {lowest_ratio:.2f}, Threshold: {1 - dynamic_threshold:.2f}")

    # So sánh với dynamic_threshold
    if lowest_ratio <= 1 - dynamic_threshold:
        best_match_levenshtein = all_sentences[min_ratio_idx]
        plagiarized_count += 1
        print(f"Câu {i + 1}: Plagiarized content detected (Levenshtein Distance):")
        print("Reference:", best_match_levenshtein)
        print()
    else:
        print(f"Câu {i + 1}: No plagiarism detected.\n")
    
# End the timer
end_time = time.time()
# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán khoảng cách Levenshtein")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")