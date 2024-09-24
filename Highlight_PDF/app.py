from flask import Flask, render_template, request, jsonify
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

@app.route("/<file_id>/on-source-highlight", methods=['POST'])
def highlight_route(file_id):
    data = request.get_json()
    school_id = data.get('school_id')
    result = highlight_school(file_id, school_id)
    file_data_view = files_collection.find_one({"file_id": int(file_id), "type": 'view_all'})
    pdf_binary_view = bytes(file_data_view['content'])
    pdf_stream_view = io.BytesIO(pdf_binary_view)
    pdf_base64_view = base64.b64encode(pdf_stream_view.getvalue()).decode('utf-8')

    return jsonify({"pdf_data_view": pdf_base64_view})

@app.route("/<file_id>/rank-source", methods=['POST'])
def rank_source(file_id):
    file_id_pdf = file_id
    sentences_data = sentences_collection.find({"file_id": int(file_id_pdf), "sources": {"$ne": None, "$ne": []}})
    
    if sentences_data:
        school_source_on = {}
        for sentence in sentences_data:
            sources = sentence.get('sources', [])
            for source in sources:
                page = sentence.get('page', None)
                sentence_index = sentence.get('sentence_index', None)
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
    school_source_on = sorted(school_source_on.items(), key=lambda x: x[1]['word_count'], reverse=True)
    
    for i, (school_id_source, _) in enumerate(school_source_on): 
        sentences_data = sentences_collection.find({"file_id": int(file_id_pdf), "sources": {"$ne": None, "$ne": []}})
        for sentence in sentences_data:
            sources = sentence.get('sources', [])
            for source in sources:
                school_id = source['school_id']
                if school_id == school_id_source:
                    collection_sentences.update_one(
                        {"_id": sentence["_id"], "sources.school_id": school_id},
                        {"$set": {"sources.$.school_stt": i + 1}}
                    )
    file_data = files_collection.find_one({"file_id": int(file_id_pdf), "type": 'raw'})
    pdf_binary = bytes(file_data['content'])
    pdf_stream = io.BytesIO(pdf_binary)
    pdf_base64 = base64.b64encode(pdf_stream.getvalue()).decode('utf-8')

    return jsonify({"pdf_base64": pdf_base64})

@app.route("/<file_id>/on-source", methods=['POST'])
def load_file_pdf(file_id):
    file_data = files_collection.find_one({"file_id": int(file_id), "type": 'raw'})

    pdf_binary = bytes(file_data['content'])
    pdf_stream = io.BytesIO(pdf_binary)
    pdf_base64 = base64.b64encode(pdf_stream.getvalue()).decode('utf-8')

    return jsonify({"pdf_base64": pdf_base64})

@app.route("/<file_id>")
def view_pdf(file_id):
    try:
        file_id_pdf = file_id
        file_data = files_collection.find_one({"file_id": int(file_id), "type": 'raw'})
        file_data_checked = files_collection.find_one({"file_id": int(file_id), "type": 'checked'})

        sentences_data = sentences_collection.find({"file_id": int(file_id), "sources": {"$ne": None, "$ne": []}})

        
        if file_data_checked and sentences_data:
            
            pdf_binary_checked = bytes(file_data_checked['content'])
            pdf_binary = bytes(file_data['content'])


            pdf_stream_checked = io.BytesIO(pdf_binary_checked)
            pdf_stream = io.BytesIO(pdf_binary)

            
            pdf_base64_checked = base64.b64encode(pdf_stream_checked.getvalue()).decode('utf-8')
            pdf_base64 = base64.b64encode(pdf_stream.getvalue()).decode('utf-8')


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


            return render_template('index.html',file_id=file_id_pdf,pdf_base64=pdf_base64, pdf_data=pdf_base64_checked, page_count = page_count, word_count = word_count, percent = percent, best_sources_list = best_sources_list, school_source_off=school_source_off, school_source_on = school_source_on )
        
        else:
            return "File not found", 404

        
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the request", 500

if __name__ == '__main__':
    app.run(debug=True)
