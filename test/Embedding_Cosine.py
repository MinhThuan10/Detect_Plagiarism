from processing_input import *
from sentence_transformers import SentenceTransformer
import numpy as np
import time


# Start the timer
start_time = time.time()
# Load the embedding model
model = SentenceTransformer('dangvantuan/vietnamese-embedding')

def embedding_vietnamese(text):
    embedding = model.encode(text)
    return embedding



sentences, search_results, all_sentence_contents, _ = search_elastic('./test/test.txt')

plagiarized_count = 0

for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]
    
    # Compute embeddings for the query and reference sentences
    query_embedding = embedding_vietnamese(preprocessed_query).reshape(1, -1)
    reference_embeddings = np.array([embedding_vietnamese(ref) for ref in preprocessed_references])

    # Calculate cosine similarity
    similarity_scores = calculate_similarity(query_embedding, reference_embeddings)

    # Calculate dynamic threshold based on sentence length
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)
    
    # Determine plagiarized content
    highest_score = 0
    best_result = None

    for j, score in enumerate(similarity_scores[0]):
        if score >= dynamic_threshold and score > highest_score:
            highest_score = score
            best_result = {
                'reference_text': all_sentence_contents[i][j],
            }

    if best_result:
        plagiarized_count += 1
        print(f"Câu {i + 1}: Plagiarized content detected:")
        print("Reference:", best_result['reference_text'])
        print(f"Score: {highest_score:.2f}, Threshold: {dynamic_threshold:.2f}")
    else:
        print(f"Câu {i + 1}: No plagiarism detected.")

# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán kết hợp với Embedding và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
