from pymongo import MongoClient
from scipy.sparse import csr_matrix
def save_to_mongodb(processed_sentences, db_name, collection_name):
    client = MongoClient('localhost', 27017)  # Kết nối tới MongoDB, chỉnh sửa theo cấu hình của bạn
    db = client[db_name]
    collection = db[collection_name]

    # Chuẩn bị dữ liệu để chèn vào MongoDB
    documents = []
    for sentence_index, (sentence, page_num) in enumerate(processed_sentences, start=1):
        document = {
            'sentence': sentence,
            'page_number': page_num,
            'sentence_index': sentence_index,  # Add sentence index
            # 'tfidf_features': features.toarray().tolist() if isinstance(features, csr_matrix) else features  # Convert to list if features is csr_matrix
        }
        documents.append(document)
    # Lưu các tài liệu vào MongoDB
    collection.insert_many(documents)