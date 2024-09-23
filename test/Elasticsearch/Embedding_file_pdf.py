import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import time
from sentence_split import *
import json
from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism_PDF']
collection_sentences = db['sentences']
collection_files = db['files']

# Start the timer
start_time = time.time()
plagiarized_count = 0
file_path = './test/Data/Ditgial_MarketingTLCK_Edit.pdf'

assignment_id = 1
file_id = 3
title = 'Ditgial_MarketingTLCK_Edit'
author = 'Thuan'


def read_pdf_binary(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def save_pdf_to_mongo(pdf_path):
    content = read_pdf_binary(pdf_path)
    result = {
        "assignment_id" : assignment_id,
        "file_id": file_id,
        "title": title,
        "author": author,
        "plagiarism": None,
        "content": content
        }
    collection_files.insert_one(result)
# save_pdf_to_mongo(file_path)

pdf_document = fitz.open(file_path)
# Lặp qua từng trang và trích xuất nội dung
for page_num in range(pdf_document.page_count):
    page = pdf_document[page_num]
    text = page.get_text("text")
    sentences = split_sentences(text)
    for i, sentence in enumerate(sentences):
        preprocessed_query, sentence_results = search_sentence_elastic(sentence)
        if preprocessed_query is None or not sentence_results:
            result = {
                "file_id" : file_id,
                "title": title,
                "page": page_num + 1,
                "sentence_index": i + 1,
                "sentence": sentence,
                "plagiarism": 'no',
                "sources": []
                }
            collection_sentences.insert_one(result)
            continue
#         preprocessed_references = [preprocess_text_vietnamese(ref['sentence'])[0] for ref in sentence_results]
#         all_sentences = [preprocessed_query] + preprocessed_references
        
#         # Tính toán embeddings cho tất cả các câu cùng một lúc
#         embeddings = embedding_vietnamese(all_sentences)

#         # Tách embedding của câu truy vấn và các câu tham chiếu
#         query_embedding = embeddings[0].reshape(1, -1)
#         reference_embeddings = embeddings[1:]
#         similarity_scores = calculate_similarity(query_embedding, reference_embeddings)

#         query_length = len(preprocessed_query.split())
#         # dynamic_threshold = calculate_dynamic_threshold(query_length)
#         dynamic_threshold = 0.1
#         max_similarity_idx = similarity_scores[0].argmax()
#         highest_score = float(similarity_scores[0][max_similarity_idx])
#         print(f"Threshold: {dynamic_threshold:.2f}")
#         sources = []
#         for idx, score in enumerate(similarity_scores[0]):
#             if score >= dynamic_threshold:
#                 school_id = sentence_results[idx]['school_id']
#                 school_name = sentence_results[idx]['school_name']
#                 file_id_source = sentence_results[idx]['file_id']
#                 file_name = sentence_results[idx]['file_name']
#                 best_match = sentence_results[idx]['sentence']

#                 word_count_sml, indices_best_match, indices_sentence = common_ordered_words_difflib(best_match, sentence)
#                 sources.append({
#                     "school_id": school_id,
#                     "school_name": school_name,
#                     "file_id": file_id_source,
#                     "file_name": file_name,
#                     "best_match": best_match,
#                     "score": float(score),
#                     "highlight": {
#                         "word_count_sml":word_count_sml,
#                         "indices_best_match": indices_best_match,
#                         "indices_sentence": indices_sentence
#                     }
#                 })

#         if sources:
#             plagiarized_count += 1
#             print(f"Câu {i + 1}: Plagiarized content detected with {len(sources)} sources.")
#             result = {
#                 "file_id" : file_id,
#                 "title": title,
#                 "sentence_index": i + 1,
#                 "sentence": sentence,
#                 "plagiarism": 'yes',
#                 "sources": sources
#             }
#         else:
#             print(f"Câu {i + 1}: No plagiarism detected.\n")
#             result = {
#                 "file_id" : file_id,
#                 "title": title,
#                 "sentence_index": i + 1,
#                 "sentence": sentence,
#                 "plagiarism": 'no',
#                 "sources": []
#             }
#         collection_sentences.insert_one(result)

# End the timer
end_time = time.time()
# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán kết hợp với Embedding và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
