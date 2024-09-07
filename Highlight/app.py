from flask import Flask, render_template
from pymongo import MongoClient
from collections import defaultdict
import io
import fitz  # PyMuPDF

app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism']
files_collection = db['files']
sentences_collection = db['sentences']


# Thêm bộ lọc base64 vào Jinja2

def get_pdf_from_mongo(file_id):
    document = files_collection.find_one({'file_id': int(file_id)})
    if document and 'content' in document:
        pdf_data = document['content']
        pdf_stream = io.BytesIO(pdf_data)
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        page_count = document['page_count']
        word_count = document['word_count']
        return pdf_document, page_count, word_count
    else:
        print("File not found")
        return None, 0, 0

@app.route("/<file_id>")
def index(file_id):
    try:
        pdf_content, page_count, word_count = get_pdf_from_mongo(file_id)
        text_html = []
        for page_num in range(pdf_content.page_count):
            page = pdf_content.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        span_text = " ".join(span["text"] for span in line["spans"])
                        text_html.append(f'<p class="text-block">{span_text}</p>')

        plagiarism_data = sentences_collection.find({'file_id': int(file_id), 'plagiarism': 'yes'})

        schools = defaultdict(lambda: {'total_word_count': 0, 'sentences': []})
        for sentence_data in plagiarism_data:
            best_matches = {}
            for source in sentence_data['sources']:
                school_name = source['school_name']
                word_count_sml = source['highlight']['word_count_sml']
                best_match = source['best_match']
                indices_sentence = source['highlight']['indices_sentence']
                indices_best_match = source['highlight']['indices_best_match']
                score = source['score']
                
                if school_name not in best_matches or best_matches[school_name]['score'] < score:
                    best_matches[school_name] = {
                        'best_match': best_match,
                        'word_count_sml': word_count_sml,
                        'indices_sentence': indices_sentence,
                        'indices_best_match': indices_best_match,
                        'score': score
                    }

            for school_name, data in best_matches.items():
                schools[school_name]['total_word_count'] += data['word_count_sml']
                schools[school_name]['sentences'].append({
                    'sentence_index': sentence_data['sentence_index'],
                    'best_match': data['best_match'],
                    'word_count_sml': data['word_count_sml'],
                    'indices_sentence': ' '.join(map(str, data['indices_sentence'])),
                    'indices_best_match': ' '.join(map(str, data['indices_best_match'])),
                })

        return render_template('index.html', text_html=''.join(text_html), page_count=page_count, word_count=word_count, schools=schools)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the request", 500

if __name__ == '__main__':
    app.run(debug=True)
