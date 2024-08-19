import requests
from bs4 import BeautifulSoup
import re
from processing import *

def embed_sentences(sentences):
    try:
        embeddings = embedding_vietnamese(sentences)
        return embeddings
    except Exception as e:
        print(f"Đã xảy ra lỗi khi tính toán embeddings: {e}")
        return None

# Ví dụ sử dụng
preprocessed_query, _ = preprocess_text_vietnamese('Điện áp ở đầu có dấu chấm của cuộn sơ cấp cao hơn đầu còn lại, gây ra hiện tượng tương tự ở cuộn thứ cấp.')
url = 'https://caselaw.vn/van-ban-phap-luat/248636-tieu-chuan-quoc-gia-tcvn-6306-1-2015-iec-60076-1-2011-ve-may-bien-ap-dien-luc-phan-1-qui-dinh-chung-nam-2015'  # Thay thế bằng URL của trang web bạn muốn lấy nội dung

response = requests.get(url)

# Kiểm tra xem yêu cầu có thành công không
if response.status_code == 200:
    # Lấy nội dung HTML của trang web
    html_content = response.text
    content = extract_text_from_html(html_content)
    sentences = split_sentences(content)
    sentences = remove_sentences(sentences)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]

    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = []
    for i, sentence in enumerate(all_sentences):
        print(f"Câu số:{i+1}")
        print(sentence)
        try:
            embedding = embedding_vietnamese([sentence])
            embeddings.append(embedding)
        except Exception as e:
            print(f"Lỗi khi tính toán embedding cho câu: {sentence}. Lỗi: {e}")
            break
else:
    print("Không thể lấy nội dung trang web.")

