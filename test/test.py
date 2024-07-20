import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from elasticsearch import Elasticsearch
from sklearn.metrics.pairwise import cosine_similarity
import json

# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
es = Elasticsearch("http://localhost:9200")
import numpy as np

def calculate_similarity(query_features, reference_features):
    print("Query features shape:", query_features.shape)
    print("Reference features shape:", reference_features.shape)
    
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

# Đọc nội dung từ file
file_path = './test/test.txt'
sentence_file = './test/test_sentence.txt'
output_file = './test/search.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    text = file.read()

# Tách thành các câu và xử lý
sentences = text.split('\n')

processed_sentences = []
all_tokens = []
search_results = []  # Mảng lưu trữ kết quả từ Elasticsearch
all_embeddings = [] 

for sentence in sentences:
    # Xử lý từng câu và lấy danh sách tokens
    processed_sentence, tokens = preprocess_text_vietnamese(sentence)
    processed_sentences.append(processed_sentence)
    all_tokens.append(tokens)

    # Tạo danh sách các field_value từ Elasticsearch
    sentence_results = []  # Mảng lưu trữ kết quả từng câu
    for token in tokens:
        res = es.search(index="plagiarism", body={"query": {"match": {"sentence": token}}})
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
    # Lưu kết quả từng câu vào mảng chung
    search_results.append(sentence_results)

# Ghi kết quả vào file
with open(sentence_file, 'w', encoding='utf-8') as file:
    for idx, sentence in enumerate(processed_sentences):
        file.write(f"Câu {idx + 1}: {sentence}\nToken: {all_tokens[idx]}\n")

# Ghi kết quả vào file
with open(output_file, 'w', encoding='utf-8') as file:
    for idx, results in enumerate(search_results):
        embeddings = [] 
        file.write(f"Câu {idx + 1}:\n")
        for result in results:
            token = result['token']
            page_number = result['page_number']
            sentence_index = result['sentence_index']
            sentence_content = result['sentence_content']
            embedding = result['embedding']
            file.write(f"Token: {token}, Elasticsearch result: Trang: {page_number}; Số câu: {sentence_index}\n Nội dung: {sentence_content}\n Embedding: {embedding}\n")
            embeddings.append(embedding)
        file.write("\n")
        all_embeddings.append(embeddings)

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('dangvantuan/vietnamese-embedding')
def embeddind_vietnamese(text):
    embedding = model.encode(text)
    return embedding


for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    processed_sentence = embeddind_vietnamese(processed_sentence)

    # Tính độ tương đồng cosine
    similarity_scores = calculate_similarity(processed_sentence, all_embeddings[i])
    print("Similarity scores:", similarity_scores)

    # Xác định nội dung có sao chép
    plagiarism_results = []

    for j, score in enumerate(similarity_scores[0]):
        if score >= 0.8:
            plagiarism_results.append({
                'reference_text': search_results[i][j].get('sentence_content'),
                'similarity_score': score
            })

    if plagiarism_results:
        print("Plagiarized content detected:")
        for result in plagiarism_results:
            print("Reference:", result['reference_text'])
            print("Similarity Score:", result['similarity_score'])
            print()
    else:
        print("No plagiarism detected.")

