from flask import Flask, render_template, send_file, request
from pymongo import MongoClient
import io

app = Flask(__name__)

# Kết nối đến MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism_PDF']  # Thay đổi tên cơ sở dữ liệu của bạn
files_collection = db['files']    # Thay đổi tên bộ sưu tập của bạn

@app.route("/pdf/<file_id>-<type>")
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

@app.route("/")
def index():
    file_id = 1  # Mặc định hiển thị file 1
    type = "raw"  # Thay đổi type theo nhu cầu
    return render_template('index.html', file_id=file_id, type=type)


if __name__ == '__main__':
    app.run(debug=True)
