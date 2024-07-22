import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
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

sentence_file = './test/test_sentence.txt'
output_file = './test/search.txt'

def search_elastic(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # Tách thành các câu và xử lý
    sentences = text.split('\n')

    processed_sentences = []
    all_tokens = []
    search_results = []  # Mảng lưu trữ kết quả từ Elasticsearch
    all_sentence_contents = [] 
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


    # Tính toán TF-IDF cho từng câu file txt
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_sentences)

    # Ghi kết quả vào file
    with open(sentence_file, 'w', encoding='utf-8') as file:
        for idx, sentence in enumerate(processed_sentences):
            file.write(f"Câu {idx + 1}: {sentence}\nToken: {all_tokens[idx]}\nTF-IDF:\n{tfidf_matrix[idx]}\n\n")

    # Ghi kết quả vào file
    with open(output_file, 'w', encoding='utf-8') as file:
        for idx, results in enumerate(search_results):
            embeddings = [] 
            sentence_contents = [] 
            file.write(f"Câu {idx + 1}:\n")
            for result in results:
                token = result['token']
                page_number = result['page_number']
                sentence_index = result['sentence_index']
                sentence_content = result['sentence_content']
                embedding = result['embedding']
                file.write(f"Token: {token}, Elasticsearch result: Trang: {page_number}; Số câu: {sentence_index}; Nội dung: {sentence_content}\n Embedding: {embedding}")
                embeddings.append(embedding)              
                sentence_contents.append(sentence_content)
            file.write("\n")
            all_sentence_contents.append(sentence_contents)
            all_embeddings.append(embeddings)
    return sentences, search_results, all_sentence_contents, all_embeddings