from pymongo import MongoClient
from elasticsearch import Elasticsearch

def save_to_mongodb(processed_sentences, file_id, file_name, db_name, collection_name):
    client = MongoClient('localhost', 27017)  # Kết nối tới MongoDB, chỉnh sửa theo cấu hình của bạn
    
    #client = MongoClient("mongodb+srv://minhthuan:minhthuan@minhthuan.vkhimqg.mongodb.net/?retryWrites=true&w=majority&appName=MinhThuan")
    db = client[db_name]
    collection = db[collection_name]

    # Chuẩn bị dữ liệu để chèn vào MongoDB
    documents = []
    for i, sentence in enumerate(processed_sentences, start=1):
        document = {
            'school_id': '1',
            'school_name': 'Ho Chi Minh City University of Technology and Education',
            'file_id': file_id,
            'file_name': file_name,
            'sentence': sentence,
            'type':'Ấn bản'
        }
        documents.append(document)
    # Lưu các tài liệu vào MongoDB
    collection.insert_many(documents)


def save_to_elasticsearch(ip_cluster, processed_sentences,school_id, school_name, file_id, file_name, index_name, type):
    # Kết nối tới Elasticsearch
    es = Elasticsearch([ip_cluster])  # Chỉnh sửa theo cấu hình của bạn

    # Chuẩn bị dữ liệu để chèn vào Elasticsearch
    for i, sentence in enumerate(processed_sentences, start=1):
        document = {
            'school_id': school_id,
            'school_name': school_name,
            'file_id': file_id,
            'file_name': file_name,
            'sentence': sentence,
            'type': type
        }
        # Lưu tài liệu vào Elasticsearch
        es.index(index=index_name, document=document)