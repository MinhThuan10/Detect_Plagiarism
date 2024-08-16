import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from processing_input import *
from sentence_transformers import SentenceTransformer
import time
import torch

# Start the timer
start_time = time.time()
# Determine device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Tải mô hình và chuyển sang GPU (nếu có)
model = SentenceTransformer('dangvantuan/vietnamese-embedding', device = device)

def embedding_vietnamese(text):
    embedding = model.encode(text)
    return embedding

plagiarized_count = 0

with open('./test/Data/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
    # Tách thành các câu và xử lý
sentences = text.split('\n')

for i, sentence in enumerate(sentences):
    preprocessed_query, all_sentences = search_sentence_elastic(sentence)

    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentences]
      
    all_sentences = [preprocessed_query] + preprocessed_references
    
    # Tính toán embeddings cho tất cả các câu cùng một lúc
    embeddings = embedding_vietnamese(all_sentences)

    # Tách embedding của câu truy vấn và các câu tham chiếu
    query_embedding = embeddings[0].reshape(1, -1)
    reference_embeddings = embeddings[1:]



    similarity_scores = calculate_similarity(query_embedding, reference_embeddings)

    # Calculate dynamic threshold based on sentence length
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
print("Đánh giá độ hiệu quả của thuật toán kết hợp với Embedding và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
