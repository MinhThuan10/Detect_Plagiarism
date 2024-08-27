import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
from save_txt import *
from processing import *
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import requests
import PyPDF2
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Bắt đầu tính thời gian
start_time = time.time()


# Đường dẫn URL của file PDF
url = 'https://m.hvtc.edu.vn/Portals/0/01_2018/3Toan%20van%20luan%20an.pdf'

# Gửi yêu cầu GET để tải về nội dung file PDF
response = requests.get(url)

# Kiểm tra nếu yêu cầu thành công
if response.status_code == 200:
    # Đọc nội dung PDF từ response
    f = io.BytesIO(response.content)
    reader = PyPDF2.PdfReader(f)

    # Lấy văn bản từ từng trang của PDF
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        text = page.extract_text()
        print(f"Page {i+1}:")
        print(text)
else:
    print(f"Không thể tải file PDF. Mã lỗi: {response.status_code}")



# embedding_vietnamese(sentences)
# Kết thúc và in ra thời gian thực hiện
end_time = time.time()
elapsed_time = end_time - start_time


print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
