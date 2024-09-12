import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import time
from sentence_split import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
from pymongo import MongoClient
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism']
collection_sentences = db['sentences']
collection_files = db['files']
collection_schools = db['schools']

# Start the timer
start_time = time.time()
plagiarized_count = 0
sentences_cache = {}


file_path = './test/Data/Ditgial_MarketingTLCK_Edit.pdf'

assignment_id = 1
file_id = 3
title = 'Ditgial_MarketingTLCK_Edit'
author = 'Thuan'


def processing_data(file_path):
    # Trích xuất nội dung văn bản từ file PDF với số trang
    text, page_count, word_count = extract_pdf_text(file_path, './output/content.txt')
    # Kết hợp các dòng và tách câu, lưu cả số trang cho mỗi câu
    sentences_with_page = combine_lines_and_split_sentences(text, './output/sentence_split.txt')
    # Loại bỏ các câu có ít hơn 1 từ
    processed_sentences = remove_single_word_sentences(sentences_with_page, './output/processed_sentences.txt')
    return processed_sentences, page_count, word_count

processed_sentences, page_count, word_count = processing_data(file_path)

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
        "content": content,
        "page_count" : page_count,
        "word_count" : word_count
        }
    collection_files.insert_one(result)
save_pdf_to_mongo(file_path)


# for i, sentence in enumerate(processed_sentences):
#     preprocessed_query, sentence_results = search_sentence_elastic(sentence)
#     if preprocessed_query is None or not sentence_results:
#         print(f"Câu {i + 1}: No results found for this sentence. Moving to the next one.")
#         result = {
#             "file_id" : file_id,
#             "title": title,
#             "sentence_index": i + 1,
#             "sentence": sentence,
#             "plagiarism": 'no',
#             "sources": []
#             }
#         collection_sentences.insert_one(result)
#         continue
#     sources = []
    
#     preprocessed_references = [preprocess_text_vietnamese(ref['sentence'])[0] for ref in sentence_results]
#     all_sentences = [preprocessed_query] + preprocessed_references
    
#     # Tính toán embeddings cho tất cả các câu cùng một lúc
#     embeddings = embedding_vietnamese(all_sentences)

#     # Tách embedding của câu truy vấn và các câu tham chiếu
#     query_embedding = embeddings[0].reshape(1, -1)
#     reference_embeddings = embeddings[1:]
#     similarity_scores = calculate_similarity(query_embedding, reference_embeddings)

#     query_length = len(preprocessed_query.split())
#     dynamic_threshold = calculate_dynamic_threshold(query_length)
    
#     max_similarity_idx = similarity_scores[0].argmax()
#     highest_score = float(similarity_scores[0][max_similarity_idx])
    
#     for idx, score in enumerate(similarity_scores[0]):
#         if score >= dynamic_threshold:
#             school_id = sentence_results[idx]['school_id']
#             school_name = sentence_results[idx]['school_name']
#             file_id_source = sentence_results[idx]['file_id']
#             file_name = sentence_results[idx]['file_name']
#             num_of_sentence = sentence_results[idx]['num_of_sentence']
#             best_match = sentence_results[idx]['sentence']

#             word_count_sml, indices_best_match, indices_sentence = common_ordered_words_difflib(best_match, sentence)
#             sources.append({
#                 "school_id": school_id,
#                 "school_name": school_name,
#                 "file_id": file_id_source,
#                 "file_name": file_name,
#                 "best_match": best_match,
#                 "score": float(score),
#                 "highlight": {
#                     "word_count_sml":word_count_sml,
#                     "indices_best_match": indices_best_match,
#                     "indices_sentence": indices_sentence
#                 }
#             })
    
#     result = search_google(preprocessed_query)
#     items = result.get('items', [])
#     all_snippets = [item.get('snippet', '') for item in items if item.get('snippet', '')]
    
#     if not all_snippets:
#         continue

#     top_similarities = compare_sentences(sentence, all_snippets)
#     for _, idx in top_similarities:
#         url = items[idx].get('link')
#         snippet = all_snippets[idx]
#         # Tìm trong cache trước khi tải nội dung
#         sentences = sentences_cache.get(url)
            
#         if sentences is None:
#             content = fetch_url(url)
#             sentences_from_webpage = split_sentences(content)
#             sentences = remove_sentences(sentences_from_webpage)
#             sentences_cache[url] = sentences

#         if sentences:             
#             snippet_parts = split_snippet(snippet)
#             # snippet_parts = remove_snippet_parts(snippet_parts)
#             # Lọc các câu chứa ít nhất một phần của snippet
#             relevant_sentences = [s for s in sentences if check_snippet_in_sentence(s, snippet_parts)]
#             if relevant_sentences:
#                 similarity_sentence, match_sentence, _ = compare_with_sentences(sentence, relevant_sentences)
#                 if similarity_sentence > dynamic_threshold:
#                     parsed_url = urlparse(url)
#                     # Lấy tên miền chính
#                     domain = parsed_url.netloc.replace('www.', '')
#                     # Kiểm tra xem trường có tồn tại chưa
#                     existing_school = collection_schools.find_one({'school_name': domain})
                    
#                     if existing_school is None:
#                         max_id_school = collection_schools.find_one(sort=[("school_id", -1)])
#                         if max_id_school:
#                             new_school_id = max_id_school['school_id'] + 1
#                         else:
#                             new_school_id = 1
#                         new_school = {
#                             'school_id': new_school_id,
#                             'school_name': domain
#                         }
#                         collection_schools.insert_one(new_school)
                        
#                         school_id = new_school_id
#                         school_name = domain
#                         file_id_source = url
#                         file_name = items[idx].get('title')
#                         best_match = match_sentence
#                     else:
#                         school_id = existing_school.get('school_id')
#                         school_name = domain
#                         file_id_source = url
#                         file_name = items[idx].get('title')
#                         best_match = match_sentence

#                     word_count_sml, indices_best_match, indices_sentence = common_ordered_words_difflib(best_match, sentence)
#                     sources.append({
#                         "school_id": school_id,
#                         "school_name": school_name,
#                         "file_id": file_id_source,
#                         "file_name": file_name,
#                         "best_match": best_match,
#                         "score": float(similarity_sentence),
#                         "highlight": {
#                             "word_count_sml":word_count_sml,
#                             "indices_best_match": indices_best_match,
#                             "indices_sentence": indices_sentence
#                         }
#                     })

#     if sources:
#         plagiarized_count += 1
#         result = {
#             "file_id" : file_id,
#             "title": title,
#             "sentence_index": i + 1,
#             "sentence": sentence,
#             "plagiarism": 'yes',
#             "sources": sources
#         }
#     else:
#         result = {
#             "file_id" : file_id,
#             "title": title,
#             "sentence_index": i + 1,
#             "sentence": sentence,
#             "plagiarism": 'no',
#             "sources": []
#         }
#     collection_sentences.insert_one(result)


def process_sentence(i, sentence):
    sources = []
    preprocessed_query, sentence_results = search_sentence_elastic(sentence)
    
    if preprocessed_query is None or not sentence_results:
        result = {
            "file_id": file_id,
            "title": title,
            "sentence_index": i + 1,
            "sentence": sentence,
            "plagiarism": 'no',
            "sources": []
        }
        collection_sentences.insert_one(result)
        return 0, None
    
    preprocessed_references = [preprocess_text_vietnamese(ref['sentence'])[0] for ref in sentence_results]
    all_sentences = [preprocessed_query] + preprocessed_references

    # Tính toán embeddings cho tất cả các câu cùng một lúc
    embeddings = embedding_vietnamese(all_sentences)
    query_embedding = embeddings[0].reshape(1, -1)
    reference_embeddings = embeddings[1:]
    similarity_scores = calculate_similarity(query_embedding, reference_embeddings)

    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)

    for idx, score in enumerate(similarity_scores[0]):
        if score >= dynamic_threshold:
            school_id = sentence_results[idx]['school_id']
            school_name = sentence_results[idx]['school_name']
            file_id_source = sentence_results[idx]['file_id']
            file_name = sentence_results[idx]['file_name']
            best_match = sentence_results[idx]['sentence']

            word_count_sml, indices_best_match, indices_sentence = common_ordered_words_difflib(best_match, sentence)
            sources.append({
                "school_id": school_id,
                "school_name": school_name,
                "file_id": file_id_source,
                "file_name": file_name,
                "best_match": best_match,
                "score": float(score),
                "highlight": {
                    "word_count_sml": word_count_sml,
                    "indices_best_match": indices_best_match,
                    "indices_sentence": indices_sentence
                }
            })

    result = search_google(preprocessed_query)
    items = result.get('items', [])
    all_snippets = [item.get('snippet', '') for item in items if item.get('snippet', '')]
    
    if not all_snippets:
        return 0, None

    top_similarities = compare_sentences(sentence, all_snippets)
    for _, idx in top_similarities:
        url = items[idx].get('link')
        snippet = all_snippets[idx]
        # Tìm trong cache trước khi tải nội dung
        sentences = sentences_cache.get(url)
            
        if sentences is None:
            content = fetch_url(url)
            sentences_from_webpage = split_sentences(content)
            sentences = remove_sentences(sentences_from_webpage)
            sentences_cache[url] = sentences

        if sentences:             
            snippet_parts = split_snippet(snippet)
            # snippet_parts = remove_snippet_parts(snippet_parts)
            # Lọc các câu chứa ít nhất một phần của snippet
            relevant_sentences = [s for s in sentences if check_snippet_in_sentence(s, snippet_parts)]
            if relevant_sentences:
                similarity_sentence, match_sentence, _ = compare_with_sentences(sentence, relevant_sentences)
                if similarity_sentence > dynamic_threshold:
                    parsed_url = urlparse(url)
                    # Lấy tên miền chính
                    domain = parsed_url.netloc.replace('www.', '')
                    # Kiểm tra xem trường có tồn tại chưa
                    existing_school = collection_schools.find_one({'school_name': domain})
                    
                    if existing_school is None:
                        max_id_school = collection_schools.find_one(sort=[("school_id", -1)])
                        if max_id_school:
                            new_school_id = max_id_school['school_id'] + 1
                        else:
                            new_school_id = 1
                        new_school = {
                            'school_id': new_school_id,
                            'school_name': domain
                        }
                        collection_schools.insert_one(new_school)
                        
                        school_id = new_school_id
                        school_name = domain
                        file_id_source = url
                        file_name = items[idx].get('title')
                        best_match = match_sentence
                    else:
                        school_id = existing_school.get('school_id')
                        school_name = domain
                        file_id_source = url
                        file_name = items[idx].get('title')
                        best_match = match_sentence

                    word_count_sml, indices_best_match, indices_sentence = common_ordered_words_difflib(best_match, sentence)
                    sources.append({
                        "school_id": school_id,
                        "school_name": school_name,
                        "file_id": file_id_source,
                        "file_name": file_name,
                        "best_match": best_match,
                        "score": float(similarity_sentence),
                        "highlight": {
                            "word_count_sml":word_count_sml,
                            "indices_best_match": indices_best_match,
                            "indices_sentence": indices_sentence
                        }
                    })

    if sources:
        result = {
            "file_id": file_id,
            "title": title,
            "sentence_index": i + 1,
            "sentence": sentence,
            "plagiarism": 'yes',
            "sources": sources
        }
        collection_sentences.insert_one(result)
        return 1, None
    else:
        result = {
            "file_id": file_id,
            "title": title,
            "sentence_index": i + 1,
            "sentence": sentence,
            "plagiarism": 'no',
            "sources": []
        }
        collection_sentences.insert_one(result)
        return 0, None
# Sử dụng ThreadPoolExecutor để chạy đa luồng cho từng câu
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_sentence, i, sentence) for i, sentence in enumerate(processed_sentences)]

    for future in as_completed(futures):
        try:
            plagiarized, _ = future.result()
            plagiarized_count += plagiarized
        except Exception as exc:
            print(f'Generated an exception: {exc}')

# End the timer
end_time = time.time()
# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của thuật toán kết hợp với Embedding và Similarity")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
