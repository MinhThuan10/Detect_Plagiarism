from pymongo import MongoClient
def save_to_mongodb(processed_sentences,  file_name, db_name, collection_name):
    client = MongoClient('localhost', 27017)  # Kết nối tới MongoDB, chỉnh sửa theo cấu hình của bạn
    
    #client = MongoClient("mongodb+srv://minhthuan:minhthuan@minhthuan.vkhimqg.mongodb.net/?retryWrites=true&w=majority&appName=MinhThuan")
    db = client[db_name]
    collection = db[collection_name]

    # Chuẩn bị dữ liệu để chèn vào MongoDB
    documents = []
    for sentence_index, (sentence, page_num, embedding) in enumerate(processed_sentences, start=1):
        document = {
            'file_name': file_name,
            'sentence': sentence,
            'page_number': page_num,
            'sentence_index': sentence_index,  # Add sentence index
            'Embedding': embedding.tolist()
        }
        documents.append(document)
    # Lưu các tài liệu vào MongoDB
    collection.insert_many(documents)