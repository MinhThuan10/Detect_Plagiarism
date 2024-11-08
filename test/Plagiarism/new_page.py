import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing import *
import time
import pymupdf  # import package PyMuPDF
import io
from sentence_split import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
from pymongo import MongoClient
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bson import Binary
from highlight import *
# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism_PDF']
collection_sentences = db['sentences']
collection_files = db['files']

# Start the timer
start_time = time.time()
plagiarized_count = 0
file_path = './test/Data/thuyettrinh.pdf'

assignment_id = 1
file_id = 4
title = 'thuyettrinh'
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
        "content": Binary(content),
        "type": 'raw'
        }
    collection_files.insert_one(result)
# save_pdf_to_mongo(file_path)

def is_within(qua_t, qua_s):
    if (qua_t[0].x >= qua_s[0].x and qua_t[0].y == qua_s[0].y and qua_t[-1].x <= qua_s[-1].x and qua_t[-1].y == qua_s[-1].y):
        return True
    else:
        return False
    
def is_position(new_position, positions):
    merged = False

    for position in positions:
        if (new_position['y_0'] == position['y_0'] and new_position['y_1'] == position['y_1']):
            if (new_position['x_0'] <= position['x_0'] and new_position['x_1'] >= position['x_1'] - 5):
                position['x_0'] = new_position['x_0']
                position['x_1'] = new_position['x_1']
                merged = True
                break
            if (new_position['x_0'] <= position['x_0'] and new_position['x_1'] >= position['x_0']): #1
                position['x_0'] = new_position['x_0']
                merged = True
                break     
            if (new_position['x_0'] >= position['x_0'] and new_position['x_1'] <= position['x_1']): #2
                merged = True
                break
            if (new_position['x_0'] >= position['x_0'] and new_position['x_0'] <= position['x_1'] + 5): #3
                position['x_1'] = new_position['x_1']
                merged = True
                break     
    return merged
def should_merge(pos1, pos2):
    # Check if positions overlap or are adjacent on the x-axis
    return not (pos1["x_1"] < pos2["x_0"] or pos1["x_0"] > pos2["x_1"])



pdf_document = fitz.open(file_path)
doc = pymupdf.open(file_path)


current_school_id = 0
school_cache = {}
sentences_cache = {}
word_count = 0
word_count_similarity = 0
sentence_index = 0
references = False


for page_num in range(pdf_document.page_count):
    page = pdf_document[page_num]
    text = page.get_text("text")

    clean_text = re.sub(r'[^A-Za-zÀ-ỹà-ỹ0-9\s]', '', text)
    result = search_google(clean_text)
    items = result.get('items', [])[:5]

    agg_sentences = []
    # top_similarities = compare_sentences(sentence, all_snippets)

    for item in items:
        url = item.get('link')
        # Tìm trong cache trước khi tải nội dung
        sentences = sentences_cache.get(url)
            
        if sentences is None:
            content = fetch_url(url)
            sentences_from_webpage = split_sentences(content)
            sentences = remove_sentences(sentences_from_webpage)
            sentences_cache[url] = sentences
    
        for sentence in sentences:
            agg_sentences.append({'url': url, 'sentence': sentence})

    all_sentences = [item['sentence'] for item in agg_sentences]

    sentences_file = split_sentences(text)
    sentences_file = remove_sentences(sentences_file)
    processed_sentences = [preprocess_text_vietnamese(sentence)[0] for sentence in sentences_file]

    if "TÀI LIỆU THAM KHẢO" in sentences_file[0].upper():
        references = True

    tokens = preprocess_text_vietnamese(text)[1]
    all_sentences = [
        sentence for sentence in all_sentences
        if any(token in sentence for token in tokens)
    ]   
    sentences_total = sentences_file + all_sentences
    number_sentence = len(sentences_file)

    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences_total]

    print(len(preprocessed_references))
    embeddings = embedding_vietnamese(preprocessed_references) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    for i in range(number_sentence):
        quotation_marks = check_type_setence(sentences_file[i])
        word_count += len(sentences_file[i].split())
        sources = []
        source_id = 0
        if processed_sentences[i] is None:
            print("Sentence Error")
            if references == False:
                result = {
                    "file_id": file_id,
                    "title": title,
                    "page": page_num,
                    "sentence_index": sentence_index,
                    "sentence": sentences_file[i],
                    "references": "no",
                    "quotation_marks": quotation_marks,
                    "sources": []
                }
                collection_sentences.insert_one(result)
            else:
                result = {
                    "file_id": file_id,
                    "title": title,
                    "page": page_num,
                    "sentence_index": sentence_index,
                    "sentence": sentences_file[i],
                    "references": "yes",
                    "quotation_marks": quotation_marks,
                    "sources": []
                }
                collection_sentences.insert_one(result)
            sentence_index = sentence_index + 1
            
            continue
        similarity_scores = calculate_similarity(embeddings[i:i+1], embeddings[number_sentence:]) 
        if similarity_scores.shape[1] == 0:
            continue

        query_length = len(processed_sentences[i].split())
        dynamic_threshold = calculate_dynamic_threshold(query_length)
        similarity_scores_flat = similarity_scores[0]
        top_indices = similarity_scores_flat.argsort()[-3:][::-1]
        for index in top_indices:
            max_similarity = similarity_scores_flat[index]
            best_match = all_sentences[index]
            url = agg_sentences[index]['url']
            
            if max_similarity > dynamic_threshold:
                parsed_url = urlparse(url)
                # Lấy tên miền chính
                domain = parsed_url.netloc.replace('www.', '')
                school_name = domain
                # Logic gán school_id
                if school_name in school_cache:
                    school_id = school_cache[school_name]
                else:
                    school_id = current_school_id
                    school_cache[school_name] = school_id
                    current_school_id += 1

                    file_id_source = url
                    file_name = ""
                    best_match = best_match

                    positions = []
                    word_count_sml, paragraphs_best_math, paragraphs = common_ordered_words(best_match, sentences_file[i])
                    
                    if word_count_sml > 3:
                        quads_sentence = page.search_for(sentences_file[i], quads=True)
                        
                        for paragraph in paragraphs:
                            quads_token = page.search_for(paragraph, quads=True)
                            for qua_s in quads_sentence:
                                for qua_t in quads_token:
                                    if is_within(qua_t, qua_s) == True:
                                        new_position = {
                                        "x_0" : qua_t[0].x,
                                        "y_0" : qua_t[0].y,
                                        "x_1" : qua_t[-1].x,
                                        "y_1" : qua_t[-1].y,
                                        }                                    
                                        if positions:
                                            merged = is_position(new_position, positions)
                                            if not merged:
                                                positions.append(new_position) 
                                        else:
                                            positions.append(new_position) 
                                    
                        best_match = wrap_paragraphs_with_color(paragraphs_best_math, best_match, school_id)
                        sources.append({
                            "source_id": source_id,
                            "school_id": school_id,
                            "school_name": domain,
                            "file_id": file_id_source,
                            "type_source": "Internet",
                            "except": 'no',
                            "color": color_hex[school_id],
                            "school_stt": 0,
                            "best_match": best_match,
                            "score": float(max_similarity),
                            "highlight": {
                                "word_count_sml": word_count_sml,
                                "paragraphs": paragraphs_best_math,
                                "position": positions
                            }
                        })
                        source_id = source_id +1

        result_sentences = search_top10_vector_elastic(embeddings[i])
        
        if result_sentences:
            print("So sánh trong dữ liệu")            
            for result_sentence in result_sentences:
                if float(result_sentence['score']) - 1.0 >= dynamic_threshold:
                    school_name = result_sentence['school_name']
                    file_id_source = result_sentence['file_name']
                    best_match = result_sentence['sentence']
                    type = result_sentence['type']
                    score = float(result_sentence['score']) - 1.0
                    
                    if school_name in school_cache:
                        school_id = school_cache[school_name]
                    else:
                        school_id = current_school_id
                        school_cache[school_name] = school_id
                        current_school_id += 1
                    positions = []
                    word_count_sml,paragraphs_best_math, paragraphs  = common_ordered_words(best_match, sentences_file[i])
                    quads_sentence = page.search_for(sentences_file[i], quads=True)
                    
                    if word_count_sml > 3:
                        for paragraph in paragraphs:
                            quads_token = page.search_for(paragraph, quads=True)
                            for qua_s in quads_sentence:
                                for qua_t in quads_token:
                                    if is_within(qua_t, qua_s) == True:
                                        new_position = {
                                        "x_0" : qua_t[0].x,
                                        "y_0" : qua_t[0].y,
                                        "x_1" : qua_t[-1].x,
                                        "y_1" : qua_t[-1].y,
                                        }
                                
                                        merged = is_position(new_position, positions)
                                        if not merged:
                                            positions.append(new_position)    
                                            
                                            
                                            
                        best_match = wrap_paragraphs_with_color(paragraphs_best_math, best_match, school_id)
                        sources.append({
                            "source_id":source_id,
                            "school_id": school_id,
                            "school_name": school_name,
                            "file_id": file_id_source,
                            "type_source": type, 
                            "except": 'no',
                            "color": color_hex[school_id],
                            "school_stt": 0,
                            "best_match": best_match,
                            "score": float(score),
                            "highlight": {
                                "word_count_sml": word_count_sml,
                                "paragraphs": paragraphs_best_math,
                                "position": positions
                            }
                        })
                        source_id = source_id+1

    
        if sources:
            if references == False:
                result = {
                    "file_id": file_id,
                    "title": title,
                    "page": page_num,
                    "sentence_index": sentence_index,
                    "sentence": sentences_file[i],
                    "references": "no",
                    "quotation_marks": quotation_marks,
                    "sources": sources
                }
                collection_sentences.insert_one(result)
            else:
                result = {
                    "file_id": file_id,
                    "title": title,
                    "page": page_num,
                    "sentence_index": sentence_index,
                    "sentence": sentences_file[i],
                    "references": "yes",
                    "quotation_marks": quotation_marks,
                    "sources": sources
                }
                collection_sentences.insert_one(result)
            plagiarized_count +=1
            
        else:
            if references == False:
                result = {
                    "file_id": file_id,
                    "title": title,
                    "page": page_num,
                    "sentence_index": sentence_index,
                    "sentence": sentence,
                    "references": "no",
                    "quotation_marks": quotation_marks,
                    "sources": []
                }
                collection_sentences.insert_one(result)
            else:
                result = {
                    "file_id": file_id,
                    "title": title,
                    "page": page_num,
                    "sentence_index": sentence_index,
                    "sentence": sentence,
                    "references": "yes",
                    "quotation_marks": quotation_marks,
                    "sources": []
                }
                collection_sentences.insert_one(result)
        
        sentence_index = sentence_index + 1

file_highlighted = highlight(file_id, ["student_Data", "Internet", "Ấn bản"])

if file_highlighted is not None:
    # Tạo một đối tượng BytesIO để lưu file PDF đã chỉnh sửa
    pdf_output_stream = io.BytesIO()
    
    # Lưu PDF từ đối tượng fitz.Document vào BytesIO
    file_highlighted.save(pdf_output_stream)
    file_highlighted.close()

    # Lưu thông tin vào MongoDB với PDF đã chỉnh sửa
    result = {
        "assignment_id": assignment_id,
        "file_id": file_id,
        "title": title,
        "author": author,
        "page_count": pdf_document.page_count,
        "word_count": word_count,
        "plagiarism": 0, 
        "content": Binary(pdf_output_stream.getvalue()),  # Lưu PDF dưới dạng Binary
        "type": 'checked',
        "source":{
            "student_data": "checked",
            "internet": "checked",
            "paper": "checked"
        },
        "fillter":{
            "references": "",
            "quotation_marks": "",
            "min_word": {
                "min_word":"",
                "minWordValue": 3
            }
        }
    }
    
    # Chèn dữ liệu vào MongoDB
    collection_files.insert_one(result)

    content = read_pdf_binary(file_path)
    result = {
        "assignment_id" : assignment_id,
        "file_id": file_id,
        "title": title,
        "author": author,
        "page_count": pdf_document.page_count,
        "word_count": word_count,
        "content": Binary(content),
        "type": 'view_all'
        }
    collection_files.insert_one(result)




# End the timer
end_time = time.time()
# Calculate the elapsed time
elapsed_time = end_time - start_time
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")