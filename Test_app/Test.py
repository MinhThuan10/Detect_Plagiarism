from pymongo import MongoClient
from bson import ObjectId

# Kết nối đến MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Plagiarism_PDF']  # Thay 'your_database' bằng tên cơ sở dữ liệu của bạn
collection = db['files']  # Thay 'your_collection' bằng tên bộ sưu tập của bạn

def fetch_pdf(pdf_id):
    # Truy vấn document chứa file PDF bằng ObjectId
    pdf_document = collection.find_one({'_id': ObjectId(pdf_id)})
    
    if pdf_document and 'content' in pdf_document:  # 'file' là trường chứa binary data
        pdf_data = pdf_document['content']  # Dữ liệu PDF dưới dạng binary
        
        # Lưu file PDF vào máy
        with open('output.pdf', 'wb') as f:
            f.write(pdf_data)
        print("PDF đã được lưu thành công.")
    else:
        print("Không tìm thấy file.")

# Gọi hàm với ObjectId của PDF bạn muốn lấy
fetch_pdf('66f31d9c0cf4bb0591c68fae')  # Thay đổi ID bằng ObjectId của bạn
