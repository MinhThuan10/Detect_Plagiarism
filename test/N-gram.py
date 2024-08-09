from processing_input import *
import time


# Start the timer
start_time = time.time()
sentences, search_results, all_sentence_contents, _ = search_elastic('./test/test.txt')
plagiarized_count = 0
for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]
    
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
        print(f"Câu {i+1}: Plagiarized content detected:")
        print("Reference:", best_result['reference_text'])
        print(highest_score)

    else:
        print(f"Câu {i+1}: No plagiarism detected.")
# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán N-gram kết hợp với TF-IDF và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
