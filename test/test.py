import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from elasticsearch import Elasticsearch
from sklearn.metrics.pairwise import cosine_similarity


# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
es = Elasticsearch("http://localhost:9200")

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
all_sentence_contents = [] 

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
            field_value_page = hit['_source']['page_number']
            field_value_index = hit['_source']['sentence_index']
            field_value_sentence = hit['_source']['sentence']
            result_info = {
                'token': token,
                'page_number': field_value_page,
                'sentence_index': field_value_index,
                'sentence_content': field_value_sentence
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
        sentence_contents = [] 
        file.write(f"Câu {idx + 1}:\n")
        for result in results:
            token = result['token']
            page_number = result['page_number']
            sentence_index = result['sentence_index']
            sentence_content = result['sentence_content']
            file.write(f"Token: {token}, Elasticsearch result: Trang: {page_number}; Số câu: {sentence_index}; Nội dung: {sentence_content}\n")
            sentence_contents.append(sentence_content)
        file.write("\n")
        all_sentence_contents.append(sentence_contents)




for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]
    
    # Tính toán TF-IDF cho câu query và các câu tham chiếu
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([preprocessed_query] + preprocessed_references)
    features_query = features[0]
    features_references = features[1:]

    # Tính độ tương đồng cosine
    similarity_scores = calculate_similarity(features_query, features_references)
    print("Similarity scores:", similarity_scores)

    # Xác định nội dung có sao chép
    plagiarism_results = []

    for j, score in enumerate(similarity_scores[0]):
        if score >= 0.8:
            plagiarism_results.append({
                'reference_text': all_sentence_contents[i][j],
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

