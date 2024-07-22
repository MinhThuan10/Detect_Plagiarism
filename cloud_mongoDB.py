from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


# Thay đổi 'your_connection_string' bằng chuỗi kết nối của bạn
connection_string = "mongodb+srv://phanminhthuan261023:HidP1WJSIuFojje7@minhthuan.vkhimqg.mongodb.net/plagiarism?retryWrites=true&w=majority&appName=MinhThuan"

try:
    # Tạo một client MongoDB
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
    
    # Kiểm tra kết nối
    # Nếu kết nối thành công, client.admin.command('ping') sẽ không gây ra lỗi
    client.admin.command('ping')
    print("Kết nối tới MongoDB thành công!")

except ServerSelectionTimeoutError as e:
    print(f"Lỗi kết nối tới MongoDB: {e}")

finally:
    # Đóng kết nối
    client.close()
