from pymongo import MongoClient
def save_to_mongodb(processed_sentences, file_id, file_name, db_name, collection_name):
    client = MongoClient('localhost', 27017)  # Kết nối tới MongoDB, chỉnh sửa theo cấu hình của bạn
    
    #client = MongoClient("mongodb+srv://minhthuan:minhthuan@minhthuan.vkhimqg.mongodb.net/?retryWrites=true&w=majority&appName=MinhThuan")
    db = client[db_name]
    collection = db[collection_name]

    # Chuẩn bị dữ liệu để chèn vào MongoDB
    documents = []
    for i, sentence in enumerate(processed_sentences, start=1):
        document = {
            'school_id': '2',
            'school_name': 'Phan Minh Thuan',
            'file_id': file_id,
            'file_name': file_name,
            'sentence': sentence,
            'num_of_sentence': i,  # Add sentence index
        }
        documents.append(document)
    # Lưu các tài liệu vào MongoDB
    collection.insert_many(documents)