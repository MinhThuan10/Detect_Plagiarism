import spacy
from elasticsearch import Elasticsearch
from sklearn.metrics.pairwise import cosine_similarity
import json

# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
es = Elasticsearch("http://localhost:9200")

def calculate_similarity(query_features, reference_features):
    # print("Query features shape:", query_features.shape)
    # print("Reference features shape:", reference_features.shape)
    
    # Check dimensions and transpose if necessary
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    # Check dimensions again after potential transposition
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores

def preprocess_text_vietnamese(text):
    # Process text with spaCy pipeline
    doc = nlp(text)
    # Filter out stopwords and punctuation, and convert to lowercase
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    # Join tokens back into a single string
    processed_text = ' '.join(tokens)
    return processed_text, tokens

sentence_file = './test/Data/test_sentence.txt'
output_file = './test/Data/search.txt'

def calculate_dynamic_threshold(length, max_threshold=0.9, min_threshold=0.7):
    if length < 10:
        return max_threshold  
    elif length > 40:
        return min_threshold  
    else:
        scaling_factor = (max_threshold - min_threshold) / (40 - 10)
        threshold = max_threshold - (length - 10) * scaling_factor
        return threshold

def search_sentence_elastic(sentence):
    # Xử lý từng câu và lấy danh sách tokens
    processed_sentence, tokens = preprocess_text_vietnamese(sentence)

    # Tạo danh sách các field_value từ Elasticsearch
    sentence_results = []  # Mảng lưu trữ kết quả từng câu
    seen_ids = set()  # Tập lưu các mongo_id đã thấy

    for token in tokens:
        res = es.search(index="plagiarism", body={
            "query": {
                "match": {"sentence": token}
            }
        })
        for hit in res['hits']['hits']:
            mongo_id = hit['_source']['mongo_id']
            
            # Nếu mongo_id chưa thấy, mới thêm vào kết quả
            if mongo_id not in seen_ids:
                seen_ids.add(mongo_id)
                log_entry = hit['_source']['log_entry']
                log_entry = log_entry.replace("=>", ":").replace("BSON::ObjectId(", "").replace(")", "").replace("'", '"')
                # Phân tích chuỗi JSON
                data = json.loads(log_entry)
                # Truy cập các giá trị
                sentence = data.get("sentence")
                sentence_index = data.get("sentence_index")
                page_number = data.get("page_number")
                file_name = data.get("file_name")
                result_info = {
                    'token': token,
                    'page_number': page_number,
                    'sentence_index': sentence_index,
                    'sentence_content': sentence,
                    'file_name': file_name,
                }
                sentence_results.append(result_info)  

    # Ghi kết quả vào file
    with open(sentence_file, 'w', encoding='utf-8') as file:
        file.write(f"Câu: {sentence}\nToken: {tokens}\n")

    # Ghi kết quả vào file
    with open(output_file, 'w', encoding='utf-8') as file:
        sentence_contents = [] 
        for result in sentence_results:
            token = result['token']
            page_number = result['page_number']
            sentence_index = result['sentence_index']
            sentence_content = result['sentence_content']
            file_name = result['file_name']
            file.write(f"Token: {token}, Elasticsearch result: File: {file_name}, Trang: {page_number}; Số câu: {sentence_index}; Nội dung: {sentence_content}\n")             
            sentence_contents.append(sentence_content)
    return processed_sentence, sentence_contents


def search_sentence_elastic_embedding(sentence): 
    # Xử lý từng câu và lấy danh sách tokens
    processed_sentence, tokens = preprocess_text_vietnamese(sentence)
    # Tạo danh sách các field_value từ Elasticsearch
    sentence_results = []  # Mảng lưu trữ kết quả từng câu
    for token in tokens:
        res = es.search(index="plagiarism_embedding", body={"query": {"match": {"sentence": token}}})
        for hit in res['hits']['hits']:
            log_entry = hit['_source']['log_entry']
            log_entry = log_entry.replace("=>", ":").replace("BSON::ObjectId(", "").replace(")", "").replace("'", '"')
            # Phân tích chuỗi JSON
            data = json.loads(log_entry)
            # Truy cập các giá trị
            sentence = data.get("sentence")
            sentence_index = data.get("sentence_index")
            page_number = data.get("page_number")
            embedding = data.get("Embedding")
            result_info = {
                'token': token,
                'page_number': page_number,
                'sentence_index': sentence_index,
                'sentence_content': sentence,
                'embedding': embedding
            }
            sentence_results.append(result_info)  
    # Ghi kết quả vào file
    with open(sentence_file, 'w', encoding='utf-8') as file:
        file.write(f"Câu: {sentence}\nToken: {tokens}\n")

    # Ghi kết quả vào file
    with open(output_file, 'w', encoding='utf-8') as file:
        embeddings = [] 
        sentence_contents = [] 
        for result in sentence_results:
            token = result['token']
            page_number = result['page_number']
            sentence_index = result['sentence_index']
            sentence_content = result['sentence_content']
            embedding = result['embedding']
            file.write(f"Token: {token}, Elasticsearch result: Trang: {page_number}; Số câu: {sentence_index}; Nội dung: {sentence_content}\n")
            embeddings.append(embedding)              
            sentence_contents.append(sentence_content)
        file.write("\n")
    return processed_sentence, sentence_contents, embeddings