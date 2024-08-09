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

sentences, search_results, all_sentence_contents, _ = search_elastic('./test/test.txt')

plagiarized_count = 0
for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]
    
    # Tính tỷ lệ Levenshtein distance giữa câu query và các câu tham chiếu
    levenshtein_scores = [levenshtein_ratio_and_distance(preprocessed_query, ref) for ref in preprocessed_references]
    # Tính ngưỡng động dựa trên chiều dài câu
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)
    # Xác định nội dung có sao chép dựa trên tỷ lệ Levenshtein
    plagiarism_results = []

    lowest_ratio = 1.0  # Tỷ lệ càng thấp thì câu càng giống nhau
    best_result_levenshtein = None

    for j, ratio in enumerate(levenshtein_scores):
        if ratio <= 1 - dynamic_threshold and ratio < lowest_ratio:
            lowest_ratio = ratio
            best_result_levenshtein = {
                'reference_text': all_sentence_contents[i][j],
                'score': ratio
            }

    # In kết quả
    if best_result_levenshtein:
        plagiarized_count += 1
        print(f"Câu {i+1}: Plagiarized content detected (Levenshtein Distance):")
        print("Reference:", best_result_levenshtein['reference_text'])
        print("Score:", best_result_levenshtein['score'])

    if not best_result_levenshtein:
        print(f"Câu {i+1}: No plagiarism detected.")


# End the timer
end_time = time.time()
# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán khoảng cách Levenshtein")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")