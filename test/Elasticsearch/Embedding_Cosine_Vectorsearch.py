import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import time
# Start the timer
start_time = time.time()
plagiarized_count = 0

with open('./test/Data/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
    # Tách thành các câu và xử lý
sentences = text.split('\n')

processed_sentences = [preprocess_text_vietnamese(sentence)[0] for sentence in sentences]

vector_sentences = embedding_vietnamese(processed_sentences)

for i, vector_sentence in enumerate(vector_sentences):
    
    result_sentences = search_vector_elastic(vector_sentence)

    # Calculate dynamic threshold based on sentence length
    query_length = len(processed_sentences[i].split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)

    if float(result_sentences['score']) - 1.0 >= dynamic_threshold:
        best_match = result_sentences['sentence']
        plagiarized_count += 1
        print(f"Câu {i + 1}: Plagiarized content detected:")
        print(f"Reference:", best_match)
        print()
        
    else:
        print(f"Câu {i + 1}: No plagiarism detected.\n")

# End the timer
end_time = time.time()
# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán kết hợp với Embedding và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
