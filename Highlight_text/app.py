from flask import Flask, render_template
from pymongo import MongoClient
from collections import defaultdict
import io
import fitz  # PyMuPDF
import base64

app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism']
files_collection = db['files']
sentences_collection = db['sentences']

def encode_base64(data):
    return base64.b64encode(data).decode('utf-8')

# Thêm bộ lọc base64 vào Jinja2
app.jinja_env.filters['b64encode'] = encode_base64

def get_pdf_from_mongo(file_id):
    document = files_collection.find_one({'file_id': int(file_id)})
    if document and 'content' in document:
        pdf_data = document['content']
        page_count = document.get('page_count', 0)
        word_count = document.get('word_count', 0)
        return page_count, word_count
    else:
        print("File not found")
        return 0, 0

def highlight_text(original_text, indices, school_id, sentence_id):
    words = original_text.split()
    highlighted = []
    i = 0
    while i < len(words):
        if i in indices:
            start = i
            while i in indices and i < len(words):
                i += 1
            highlighted.append(f'<span class="highlight_school{school_id} highlight highlight_sentence{sentence_id}">{" ".join(words[start:i])}</span>')
        else:
            highlighted.append(words[i])
            i += 1
    return " ".join(highlighted)

@app.route("/<file_id>")
def index(file_id):
    try:
        plagiarism_data = []
        plagiarism_details = []
        page_count, word_count = get_pdf_from_mongo(file_id)
        plagiarisms = sentences_collection.find({'file_id': int(file_id)})
        schools = defaultdict(lambda: {'school_name':'', 'total_word_count': 0, 'sentences': []})
        schools_detail = defaultdict(lambda: {'school_name':'', 'total_word_count': 0, 'sentences': []})
        
        for doc in plagiarisms:
            plagiarism = []
            plagiarism_detail = []

            sentence_id = doc['sentence_index']
            if doc['plagiarism'] == 'no':
                plagiarism.append([doc['sentence'], 0, 0, sentence_id])
                plagiarism_detail.append([doc['sentence'], 0, 0, sentence_id])

            else:
                best_matches = {}
                best_score = -1
                best_matches_data = {}
                for source in doc['sources']:
                    school_id = source.get('school_id', 'Unknown')
                    school_name = source.get('school_name')
                    word_count_sml = source.get('highlight', {}).get('word_count_sml', 0)
                    best_match = source.get('best_match', '')
                    indices_sentence = source.get('highlight', {}).get('indices_sentence', [])
                    indices_best_match = source.get('highlight', {}).get('indices_best_match', [])
                    score = source.get('score', 0)
                    
                    highlighted_sentence = highlight_text(doc['sentence'], indices_sentence, school_id, sentence_id)
                    highlighted_best_match = highlight_text(best_match, indices_best_match, school_id, sentence_id)
                    
                    # Cập nhật thông tin trường học có điểm số cao nhất
                    if score > best_score:
                        best_score = score
                        best_matches_data = {
                            'school_id': school_id,
                            'school_name': school_name,
                            'highlighted_sentence': highlighted_sentence,
                            'highlighted_best_match': highlighted_best_match,
                            'word_count_sml': word_count_sml,
                            'score': score
                        }

                    if school_id not in best_matches or best_matches[school_id]['score'] < score:
                        best_matches[school_id] = {
                            'school_name': school_name,
                            'highlighted_sentence': highlighted_sentence,
                            'highlighted_best_match': highlighted_best_match,
                            'word_count_sml': word_count_sml,
                            'score': score
                        }

                # Kiểm tra xem best_matches_data đã tồn tại trong schools_detail chưa
                if best_matches_data.get('school_id') not in schools_detail:
                    schools_detail[best_matches_data['school_id']] = {
                        'total_word_count': 0,
                        'school_name': best_matches_data['school_name'],
                        'sentences': []
                    }

                schools_detail[best_matches_data['school_id']]['total_word_count'] += best_matches_data['word_count_sml']
                schools_detail[best_matches_data['school_id']]['sentences'].append({
                    'best_match': best_matches_data['highlighted_best_match'],
                    'sentence': best_matches_data['highlighted_sentence'],
                    'word_count_sml': best_matches_data['word_count_sml'],
                    'sentence_index': sentence_id

                })
                schools_detail[best_matches_data['school_id']]['sentences'].sort(key=lambda x: x['sentence_index'])

                plagiarism_detail = [[best_matches_data['highlighted_sentence'], best_matches_data['word_count_sml'], best_matches_data['school_id'], sentence_id]]


                # Giả sử `best_matches` là một dictionary với `school_id` là khóa và `data` là giá trị
                for school_id, data in best_matches.items():
                    # Cập nhật thông tin trường học
                    if school_id not in schools:
                        schools[school_id] = {
                            'total_word_count': 0,
                            'school_name': data['school_name'],
                            'sentences': []
                        }

                    schools[school_id]['total_word_count'] += data['word_count_sml']
                    schools[school_id]['sentences'].append({
                        'best_match': data['highlighted_best_match'],
                        'sentence': data['highlighted_sentence'],
                        'word_count_sml': data['word_count_sml'],
                        'sentence_index': sentence_id
                    })
                    plagiarism.append([data['highlighted_sentence'], data['word_count_sml'], school_id, sentence_id])
                    schools[school_id]['sentences'].sort(key=lambda x: x['sentence_index'])
            
            plagiarism_details.append(plagiarism_detail)

            plagiarism_data.append(plagiarism)

        return render_template('index.html', plagiarisms=plagiarism_data, plagiarism_details=plagiarism_details, page_count=page_count, word_count=word_count, schools=schools, schools_detail=schools_detail)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the request", 500

if __name__ == '__main__':
    app.run(debug=True)
