import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import time
from sklearn.feature_extraction.text import TfidfVectorizer


# Start the timer
start_time = time.time()
plagiarized_count = 0
with open('./test/Data/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
    # Tách thành các câu và xử lý
sentences = text.split('\n')

for i, sentence in enumerate(sentences):
    preprocessed_query, all_sentences= search_sentence_elastic(sentence)

    preprocessed_references = [preprocess_text_vietnamese(ref['sentence'])[0] for ref in all_sentences]  
    # Tính toán TF-IDF cho câu query và các câu tham chiếu với N-gram
    vectorizer = TfidfVectorizer(ngram_range=(2, 2))  # Sử dụng bigram (2-gram)
    features = vectorizer.fit_transform([preprocessed_query] + preprocessed_references)
    features_query = features[0]
    features_references = features[1:]

    # Tính độ tương đồng cosine
    similarity_scores = calculate_similarity(features_query, features_references)
    # Tính ngưỡng động dựa trên chiều dài câu
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)
    
    max_similarity_idx = similarity_scores[0].argmax()
    # Lấy giá trị similarity cao nhất
    highest_score = similarity_scores[0][max_similarity_idx]
    print(f"Score: {highest_score:.2f}, Threshold: {dynamic_threshold:.2f}")
    # So sánh với dynamic_threshold
    if highest_score >= dynamic_threshold:
        best_match = all_sentences[max_similarity_idx]
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
print("Đánh giá độ hiệu quả của thuật toán N-gram kết hợp với TF-IDF và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
