from io import BytesIO
from pymongo import MongoClient

def get_pdf_from_mongo(file_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Plagiarism']
    collection = db['files']
    file_id = int(file_id)

    document = collection.find_one({'file_id': file_id})
    if document and 'content' in document:
        pdf_data = document['content']
        page_count = document['page_count']
        word_count = document['word_count']
        return BytesIO(pdf_data), page_count, word_count
    else:
        print("File not found")
        return None
    
a, b, c = get_pdf_from_mongo(1)

print(b)
print(c)