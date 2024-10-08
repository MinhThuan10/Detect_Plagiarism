from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from pymongo import MongoClient
import io
import base64
from bson import Binary

app = Flask(__name__)

import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from highlight import highlight as hihighlight_pdf, highlight_school

# Sử dụng các hàm hoặc class từ highlight.py

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism_PDF']
files_collection = db['files']
sentences_collection = db['sentences']



def update_school_stt(file_id, type, type_sources):
    # update STT
    file_id_pdf = file_id
    sentences_data = sentences_collection.find({"file_id": int(file_id_pdf),
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})
    school_source = {}
    minWordValue = files_collection.find_one({"file_id": int(file_id_pdf), "type": 'checked'}).get('fillter', {}).get('min_word', {}).get('minWordValue', 0)

    print(minWordValue)
    if sentences_data:
        if type == "best_source":
            for sentence in sentences_data:
                    sources = sentence.get('sources', [])
                    # filtered_sources = [source for source in sources if (source['except'] == 'no' and source['type_source'] in type_sources)]
                    filtered_sources = [
                        source for source in sources 
                        if (source['except'] == 'no' and 
                            source['type_source'] in type_sources and 
                            source.get('highlight', {}).get('word_count_sml', 0) >= int(minWordValue))
                    ]
                    if filtered_sources:
                        source_max = max(filtered_sources, key=lambda x: x['score'])
                        school_id = source_max['school_id']
                        highlight_source = source_max['highlight']
                        if school_id not in school_source:
                            school_source[school_id] = {
                                "word_count": 0, 
                            }
                        school_source[school_id]['word_count'] += highlight_source.get('word_count_sml', 0)
        else:
            if type == "view_all":
                for sentence in sentences_data:
                    sources = sentence.get('sources', [])
                    # filtered_sources = [source for source in sources if (source['except'] == 'no' and source['type_source'] in type_sources)]
                    filtered_sources = [
                        source for source in sources 
                        if (source['except'] == 'no' and 
                            source['type_source'] in type_sources and 
                            source.get('highlight', {}).get('word_count_sml', 0) >= int(minWordValue))
                    ]
                    if filtered_sources:
                        for source in filtered_sources:
                            school_id = source['school_id']
                            highlight_source = source['highlight']
                            if school_id not in school_source:
                                school_source[school_id] = {
                                    "word_count": 0, 
                                }
                            school_source[school_id]['word_count'] += highlight_source.get('word_count_sml', 0)
        school_source = sorted(school_source.items(), key=lambda x: x[1]['word_count'], reverse=True)

    word_count = files_collection.find_one({"file_id": int(file_id_pdf), "type": 'checked'}).get('word_count', 0)
    word_count_sml = 0
    if school_source:
        for i, (school_id_source, source_data) in enumerate(school_source):
            # Lặp qua từng câu để tìm nguồn
            sentences_data = sentences_collection.find({"file_id": int(file_id_pdf),
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})
            if source_data.get('word_count', 0) > word_count/200:
                for sentence in sentences_data:
                    sources = sentence.get('sources', [])
                    for source in sources:
                        school_id_data = source['school_id']
                        if school_id_data == school_id_source:
                            sentences_collection.update_many(
                                {"file_id": int(file_id_pdf), "sources.school_id": school_id_data},
                                {"$set": {"sources.$[elem].school_stt": i + 1}}, 
                                array_filters=[{"elem.school_id": school_id_data}]
                            )
                            break
            else:
                for sentence in sentences_data:
                    sources = sentence.get('sources', [])
                    for source in sources:
                        school_id_data = source['school_id']
                        if school_id_data == school_id_source:
                            sentences_collection.update_many(
                                {"file_id": int(file_id_pdf), "sources.school_id": school_id_data},
                                {"$set": {"sources.$[elem].except": "except"}}, 
                                array_filters=[{"elem.school_id": school_id_data}]
                            )
                            break
    
    sentences_data = sentences_collection.find({"file_id": int(file_id_pdf),
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})
    if sentences_data:
        for sentence in sentences_data:
                sources = sentence.get('sources', [])
                filtered_sources = [
                    source for source in sources 
                    if (source['except'] == 'no' and 
                        source['type_source'] in type_sources and 
                        source.get('highlight', {}).get('word_count_sml', 0) >= int(minWordValue))
                ]

                if filtered_sources:
                    source_max = max(filtered_sources, key=lambda x: x['score'])
                    word_count_sml = word_count_sml +  source_max['highlight'].get('word_count_sml', 0)
    result = {
        "plagiarism": word_count_sml/word_count * 100,  # Lưu PDF dưới dạng Binary
    }
    files_collection.update_one(
                {"file_id": int(file_id_pdf), "type": "checked"},  
                {"$set": result}  # Thay đổi nội dung file
            )

    return school_source

@app.route("/pdf/<file_id>/view_all/<school_id>", methods=['GET'])
def highlight_route(file_id, school_id):
    file_checked = files_collection.find_one({"file_id": int(file_id), "type": "checked"})
    source = file_checked.get('source')
    type_source = []
    if source['student_data'] == "checked":
        type_source.append('student_Data')
    if source['internet'] == "checked":
        type_source.append('Internet')
    if source['paper'] == "checked":
        type_source.append("Ấn bản")
    result = highlight_school(file_id, school_id, type_source)
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
    file_id_pdf = file_id
    file_checked = files_collection.find_one({"file_id": int(file_id), "type": "checked"})
    source = file_checked.get('source')
    type_source = []
    if source['student_data'] == "checked":
        type_source.append('Dữ liệu học viên')
    if source['internet'] == "checked":
        type_source.append('Internet')
    if source['paper'] == "checked":
        type_source.append("Ấn bản")

    if type == 'checked':
        update_stt = update_school_stt(file_id_pdf, "best_source", type_source)
        # Tìm tệp PDF trong MongoDB theo file_id
        file_highlighted = hihighlight_pdf(int(file_id_pdf), type_source)
        if file_highlighted is not None:
            # Tạo một đối tượng BytesIO để lưu file PDF đã chỉnh sửa
            pdf_output_stream = io.BytesIO()
            # Lưu PDF từ đối tượng fitz.Document vào BytesIO
            file_highlighted.save(pdf_output_stream)
            file_highlighted.close()
            # Lưu thông tin vào MongoDB với PDF đã chỉnh sửa
            result = {
                "content": Binary(pdf_output_stream.getvalue()),  # Lưu PDF dưới dạng Binary
            }
            files_collection.update_one(
                {"file_id": int(file_id_pdf), "type": type},  # Điều kiện cập nhật
                {"$set": result}  # Thay đổi nội dung file
            )

        file_data = files_collection.find_one({"file_id": int(file_id_pdf), "type": type})
        
        if file_data:
            # Chuyển đổi nội dung tệp PDF thành bytes
            pdf_binary = bytes(file_data['content'])
            pdf_stream = io.BytesIO(pdf_binary)
            return send_file(pdf_stream, mimetype='application/pdf')
        else:
            return "File not found", 404
    else:
        if type == 'raw':
            update_stt = update_school_stt(file_id, "view_all", type_source)
            file_data = files_collection.find_one({"file_id": int(file_id_pdf), "type": 'raw'})
            if file_data:
                # Chuyển đổi nội dung tệp PDF thành bytes
                pdf_binary = bytes(file_data['content'])
                pdf_stream = io.BytesIO(pdf_binary)
                return send_file(pdf_stream, mimetype='application/pdf')
            else:
                return "File not found", 404

@app.route("/pdf/<file_id>/remove/<school_id>", methods=['POST'])
def remove_source_school(file_id, school_id):
    sentences_collection.update_many(
        {"file_id": int(file_id), "sources.school_id": int(school_id), "sources.except": "no"},
        {"$set": {"sources.$[elem].except": "source"}},
        array_filters=[{"elem.school_id": int(school_id), "elem.except": "no"}]
    )
    
    return jsonify({'success': True, 'message': 'School source removed successfully.'}), 200

@app.route("/pdf/<file_id>/add/<school_id>", methods=['POST'])
def add_source_school(file_id, school_id):
    if school_id == 'all-source':
        sentences_collection.update_many(
            {"file_id": int(file_id), "sources.except": "source"},
            {"$set": {"sources.$[elem].except": "no"}},
            array_filters=[{"elem.except": "source"}]
        )
    else:
        if school_id == 'all-text':
            sentences_collection.update_many(
                {"file_id": int(file_id), "sources.except": "text"},
                {"$set": {"sources.$[elem].except": "no"}},
                array_filters=[{"elem.except": "text"}]
            )
        else:
            sentences_collection.update_many(
                {"file_id": int(file_id), "sources.school_id": int(school_id), "sources.except": "source"},
                {"$set": {"sources.$[elem].except": "no"}},
                array_filters=[{"elem.school_id": int(school_id), "elem.except": "source"}]
            )
    return jsonify({'success': True, 'message': 'School source removed successfully.'}), 200


@app.route("/pdf/<file_id>/remove/<school_id>and<sentence_index>", methods=['POST'])
def remove_source_school_text(file_id, school_id, sentence_index):

    sentences_collection.update_many(
        {"file_id": int(file_id), "sentence_index": int(sentence_index), "sources.school_id": int(school_id),"sources.except": "no"},
        {"$set": {"sources.$[elem].except": "text"}},
        array_filters=[{"elem.school_id": int(school_id), "elem.except": "no"}]
    )

    return jsonify({'success': True, 'message': 'School source removed successfully.'}), 200

@app.route("/pdf/<file_id>/add/<sentence_index>and<source_id>", methods=['POST'])
def add_source_text(file_id, sentence_index, source_id):

    sentences_collection.update_many(
        {"file_id": int(file_id), "sentence_index": int(sentence_index), "sources.source_id": int(source_id),"sources.except": "text"},
        {"$set": {"sources.$[elem].except": "no"}},
        array_filters=[{"elem.source_id": int(source_id), "elem.except": "text"}]
    )

    return jsonify({'success': True, 'message': 'School source removed successfully.'}), 200


@app.route("/pdf/<file_id>/fillter/<studentData>-<internet>-<paper>-<references>-<curlybracket>-<minWord>-<minWordValue>", methods=['POST'])
def apply_filter(file_id, studentData, internet, paper, references, curlybracket, minWord, minWordValue):
    if studentData == "true":
        studentData = "checked"
    else:
        studentData = "no"

    if internet == "true":
        internet = "checked"
    else:
        internet = "no"

    if paper == "true":
        paper = "checked"
    else:
        paper = "no"

    if references == "true":
        references = "checked"
        sentences_collection.update_many(
            {"file_id": int(file_id), "references": "yes"},
            {"$set": {"references": "checked"}}
        )

    else:
        sentences_collection.update_many(
            {"file_id": int(file_id), "references": "checked"},
            {"$set": {"references": "yes"}}
        )
        references = "no"

    if curlybracket == "true":
        curlybracket = "checked"
        
        sentences_collection.update_many(
            {"file_id": int(file_id), "quotation_marks": "yes"},
            {"$set": {"quotation_marks": "checked"}}
        )
    else:
        curlybracket = "no"
        sentences_collection.update_many(
            {"file_id": int(file_id), "quotation_marks": "checked"},
            {"$set": {"quotation_marks": "yes"}}
        )

    if minWord == "true":
        minWord = "checked"
        
    else:
        minWord = "no"
    
    result = {
        "source.student_data": studentData,
        "source.internet": internet,
        "source.paper": paper,
        "fillter.references": references,
        "fillter.quotation_marks": curlybracket,
        "fillter.min_word.min_word": minWord,
        "fillter.min_word.minWordValue": minWordValue,



    }
    files_collection.update_one(
                {"file_id": int(file_id), "type": "checked"},  
                {"$set": result} 
            )

    return jsonify({'success': True, 'message': 'School source removed successfully.'}), 200
    
@app.route("/<file_id>")
def index(file_id):
    try:
        file_id_pdf = file_id
        file_data_checked = files_collection.find_one({"file_id": int(file_id_pdf), "type": 'checked'})
        sentences_data = sentences_collection.find({"file_id": int(file_id_pdf),
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})
        if sentences_data:
            page_count = file_data_checked.get('page_count')
            word_count = file_data_checked.get('word_count')
            percent   = file_data_checked.get('plagiarism')  
            source_file   = file_data_checked.get('source')  
            fillter_file   = file_data_checked.get('fillter')  
            minWordValue   = file_data_checked.get('fillter').get('min_word').get('minWordValue')



            type_sources = []
            if source_file['student_data'] == "checked":
                type_sources.append('Dữ liệu học viên')
            if source_file['internet'] == "checked":
                type_sources.append('Internet')
            if source_file['paper'] == "checked":
                type_sources.append("Ấn bản")

            school_source_off = {}
            school_source_on = {}
            school_exclusion_source = {}
            school_exclusion_text = {}


            # Top School
            for sentence in sentences_data:
                sources = sentence.get('sources', [])
                page = sentence.get('page', None)
                sentence_index = sentence.get('sentence_index', None)
                if sources:
                    # OFF
                    # filtered_no = [source for source in sources if (source['except'] == 'no' and source['type_source'] in type_sources)]
                    filtered_no = [
                        source for source in sources 
                        if (source['except'] == 'no' and 
                            source['type_source'] in type_sources and 
                            source.get('highlight', {}).get('word_count_sml', 0) >= int(minWordValue))
                    ]

                    if filtered_no:
                        best_source = max(filtered_no, key=lambda x: x['score'])
                        school_id = best_source['school_id']
                        school_name = best_source['school_name']
                        color = best_source['color']
                        type_source = best_source['type_source']
                        file_id = best_source['file_id']
                        best_match = best_source['best_match']
                        highlight = best_source['highlight']

                        if type_source in type_sources:
                            if school_id not in school_source_off:
                                    school_source_off[school_id] = {
                                        "school_name": school_name,
                                        "word_count": 0,
                                        "color": color,
                                        "type_source":type_source,
                                        "sentences": {}  
                                    }
                            school_source_off[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                            school_source_off[school_id]['sentences'][sentence_index] = {
                                "page": page,
                                "file_id": file_id,
                                "best_match": best_match,
                                "word_count_sml": highlight.get('word_count_sml', 0),
                                "paragraphs": highlight.get('paragraphs'),
                            }
                    

                        # ON

                        for source in filtered_no:
                            school_id = source['school_id']
                            school_name = source['school_name']
                            color = source['color']
                            type_source = source['type_source']
                            file_id = source['file_id']
                            best_match = source['best_match']
                            highlight = source['highlight']

                            if type_source in type_sources:
                                if school_id not in school_source_on:
                                    school_source_on[school_id] = {
                                        "school_name": school_name,
                                        "word_count": 0,
                                        "color": color,
                                        "type_source":type_source,
                                        "sentences": {}  
                                    }
                                school_source_on[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                                school_source_on[school_id]['sentences'][sentence_index] = {
                                    "page": page,
                                    "file_id": file_id,
                                    "best_match": best_match,
                                    "word_count_sml": highlight.get('word_count_sml', 0),
                                    "paragraphs": highlight.get('paragraphs'),
                                }

                    # filtered_sources = [source for source in sources if (source['except'] == 'source' and source['type_source'] in type_sources)]
                    filtered_sources = [
                        source for source in sources 
                        if (source['except'] == 'no' and 
                            source['type_source'] in type_sources and 
                            source.get('highlight', {}).get('word_count_sml', 0) >= int(minWordValue))
                    ]
                    if filtered_sources:
                        for source in filtered_sources:
                            school_id = source['school_id']
                            school_name = source['school_name']
                            if school_id not in school_exclusion_source:
                                school_exclusion_source[school_id] = {
                                    "school_name": school_name,
                                }

                    filtered_text = [source for source in sources if (source['except'] == 'text' and source['type_source'] in type_sources)]
                    if filtered_text :
                        for source in filtered_text :
                            sentence_index = sentence.get('sentence_index', "")
                            school_name = source['school_name']
                            best_match = source['best_match']
                            source_id = source['source_id']

                            if sentence_index not in school_exclusion_text:
                                school_exclusion_text[sentence_index] = {}  # Khởi tạo nếu chưa có

                            school_exclusion_text[sentence_index][source_id] = {
                                "school_name": school_name,
                                "best_match": best_match,
                            }
            school_source_off = sorted(school_source_off.items(), key=lambda x: x[1]['word_count'], reverse=True)

            school_source_on = sorted(school_source_on.items(), key=lambda x: x[1]['word_count'], reverse=True)


            return render_template('index.html',file_id=file_id_pdf, page_count = page_count, word_count = word_count, percent = percent, school_source_off=school_source_off, school_source_on = school_source_on, school_exclusion_source = school_exclusion_source, school_exclusion_text = school_exclusion_text, source_file = source_file, fillter_file = fillter_file )
        
        else:
            return "File not found", 404

        
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the request", 500

if __name__ == '__main__':
    app.run(debug=True)
