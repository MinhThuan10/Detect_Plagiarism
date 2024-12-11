import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import preprocess_text_vietnamese, embedding_vietnamese, search_vector_elastic, calculate_dynamic_threshold, calculate_similarity
import time
import numpy as np
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
    query_length = len(processed_sentences[i].split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)

    if result_sentences:
        vector_sentence = vector_sentence.reshape(1, -1)
        result_sentences_vector = np.array([ref['vector'] for ref in result_sentences])

        similarity_scores = calculate_similarity(vector_sentence, result_sentences_vector)
        max_similarity_idx = similarity_scores[0].argmax()
        highest_score = similarity_scores[0][max_similarity_idx]
        if highest_score >= dynamic_threshold:
            best_match = result_sentences[max_similarity_idx]['sentence']
            plagiarized_count += 1
            print(f"Câu {i + 1}: Plagiarized content detected:")
            print(f"Reference:", best_match)
            print()
                
        else:
            print(f"Câu {i + 1}: No plagiarism detected.\n")

# End the timer
end_time = time.time()
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán kết hợp với Embedding và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
