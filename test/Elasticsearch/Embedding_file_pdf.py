import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import time
from sentence_split import *
from save_txt import *

# Start the timer
start_time = time.time()
plagiarized_count = 0
file_path = './Data/SKL007296.pdf'

def processing_data(file_path):
    # Trích xuất nội dung văn bản từ file PDF với số trang
    text_with_page = extract_pdf_text(file_path)
    # Lưu nội dung vào file văn bản với số trang
    save_text_with_page_to_file(text_with_page, './output/content.txt')
    # Kết hợp các dòng và tách câu, lưu cả số trang cho mỗi câu
    sentences_with_page = combine_lines_and_split_sentences(text_with_page)
    # Lưu nội dung vào file văn bản với số dòng và số trang
    save_combined_text_with_page_to_file(sentences_with_page, './output/sentence_split.txt')
    # Loại bỏ các câu có ít hơn 1 từ
    processed_sentences = remove_single_word_sentences(sentences_with_page)
    # Lưu nội dung vào file văn bản
    save_combined_text_with_page_to_file(processed_sentences, './output/processed_sentences.txt')
    return processed_sentences

processed_sentences = processing_data(file_path)

for i, (sentence, page_num) in enumerate(processed_sentences):
    preprocessed_query, all_sentences = search_sentence_elastic(sentence)
    if preprocessed_query is None:
        print(f"Câu {i + 1}: No results found for this sentence. Moving to the next one.")
        continue
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
