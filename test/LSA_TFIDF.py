from processing_input import *
from sklearn.decomposition import TruncatedSVD
import time


# Start the timer
start_time = time.time()
sentences, _, all_sentence_contents, _ = search_elastic('./test/test.txt')

plagiarized_count = 0
for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]
    
    # Tính toán TF-IDF cho câu query và các câu tham chiếu
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([preprocessed_query] + preprocessed_references)
    
    # Áp dụng TruncatedSVD để thực hiện LSA
    n_components = min(100, features.shape[1] - 1)  # Ensure n_components <= n_features
    svd = TruncatedSVD(n_components=n_components)
    features_lsa = svd.fit_transform(features)
    
    features_query_lsa = features_lsa[0].reshape(1, -1)
    features_references_lsa = features_lsa[1:]

    # Tính độ tương đồng cosine
    similarity_scores = calculate_similarity(features_query_lsa, features_references_lsa)
    # Tính ngưỡng động dựa trên chiều dài câu
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)
    
    # Xác định nội dung có sao chép
    plagiarism_results = []

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
        print(f"Câu thứ {i + 1}: ****Plagiarized content detected:")
        print("Reference:", best_result['reference_text'])
        print(highest_score)
    else:
        print(f"Câu thứ {i + 1}: ****No plagiarism detected.")


# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán LSA (TF-IDF, SVD và Similarity)")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")