from pymongo import MongoClient


plagiarism_data = []
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism']
files_collection = db['files']
sentences_collection = db['sentences']
plagiarisms = sentences_collection.find({'file_id': 1})
for i, doc in enumerate(plagiarisms):
    sentence_id = doc['sentence_index']
    if doc['plagiarism'] == 'yes':
        plagiarism = []
        for source in doc['sources']:
            plagiarism.append([doc['sentence'], None, sentence_id])

        plagiarism_data.append(plagiarism)

print(plagiarism_data)