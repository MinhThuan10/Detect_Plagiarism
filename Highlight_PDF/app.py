from flask import Flask, render_template, request, jsonify, send_file
from pymongo import MongoClient
import io
import base64
app = Flask(__name__)

import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from highlight import *

# Sử dụng các hàm hoặc class từ highlight.py

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism_PDF']
files_collection = db['files']
sentences_collection = db['sentences']


@app.route("/pdf/<file_id>/<school_id>", methods=['POST'])
def highlight_route(file_id, school_id):
    data = request.get_json()
    result = highlight_school(file_id, school_id)
    file_data = files_collection.find_one({"file_id": int(file_id), "type": "view_all"})
    if file_data:
        # Chuyển đổi nội dung tệp PDF thành bytes
        pdf_binary = bytes(file_data['content'])
        pdf_stream = io.BytesIO(pdf_binary)
        return send_file(pdf_stream, mimetype='application/pdf')
    else:
        return "File not found", 404
    
@app.route("/pdf/<file_id>/<type>", methods=['GET'])
def view_pdf(file_id, type):
    # Tìm tệp PDF trong MongoDB theo file_id
    file_data = files_collection.find_one({"file_id": int(file_id), "type": type})
    
    if file_data:
        # Chuyển đổi nội dung tệp PDF thành bytes
        pdf_binary = bytes(file_data['content'])
        pdf_stream = io.BytesIO(pdf_binary)
        return send_file(pdf_stream, mimetype='application/pdf')
    else:
        return "File not found", 404


@app.route("/<file_id>/<type>")
def index(file_id, type):
    try:
        file_id_pdf = file_id
        file_data_checked = files_collection.find_one({"file_id": int(file_id_pdf), "type": type})
        sentences_data = sentences_collection.find({"file_id": int(file_id_pdf), "sources": {"$ne": None, "$ne": []}})
        if sentences_data:
            page_count = file_data_checked.get('page_count')
            word_count = file_data_checked.get('word_count')
            percent   = file_data_checked.get('plagiarism')    
            best_sources_list = []
            school_source_off = {}
            school_source_on = {}


            # #Top School
            for sentence in sentences_data:
                sources = sentence.get('sources', [])
            
                if sources:
                    # OFF
                    best_source = max(sources, key=lambda x: x['score'])
                    page = sentence.get('page', None)
                    sentence_index = sentence.get('sentence_index', None)
                    school_id = best_source['school_id']
                    school_name = best_source['school_name']
                    color = best_source['color']
                    file_id = best_source['file_id']
                    file_name = best_source['file_name']
                    best_match = best_source['best_match']
                    highlight = best_source['highlight']

                    if school_id not in school_source_off:
                            school_source_off[school_id] = {
                                "school_name": school_name,
                                "word_count": 0,
                                "color": color,
                                "sentences": {}  
                            }
                    school_source_off[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                    school_source_off[school_id]['sentences'][sentence_index] = {
                        "page": page,
                        "file_name": file_name,
                        "best_match": best_match,
                        "word_count_sml": highlight.get('word_count_sml', 0),
                        "paragraphs": highlight.get('paragraphs'),
                    }
                    

                    # ON

                    for source in sources:
                        school_id = source['school_id']
                        school_name = source['school_name']
                        color = source['color']
                        file_id = source['file_id']
                        file_name = source['file_name']
                        best_match = source['best_match']
                        highlight = source['highlight']
                        if school_id not in school_source_on:
                            school_source_on[school_id] = {
                                "school_name": school_name,
                                "word_count": 0,
                                "color": color,
                                "sentences": {}  
                            }
                        school_source_on[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                        school_source_on[school_id]['sentences'][sentence_index] = {
                            "page": page,
                            "file_name": file_name,
                            "best_match": best_match,
                            "word_count_sml": highlight.get('word_count_sml', 0),
                            "paragraphs": highlight.get('paragraphs'),
                        }

            school_source_off = sorted(school_source_off.items(), key=lambda x: x[1]['word_count'], reverse=True)

            school_source_on = sorted(school_source_on.items(), key=lambda x: x[1]['word_count'], reverse=True)


            return render_template('index.html',file_id=file_id_pdf, type=type, page_count = page_count, word_count = word_count, percent = percent, best_sources_list = best_sources_list, school_source_off=school_source_off, school_source_on = school_source_on )
        
        else:
            return "File not found", 404

        
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the request", 500

if __name__ == '__main__':
    app.run(debug=True)
