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
url = 'https://www.eajournals.org/wp-content/uploads/Plagiarism.pdf'  

response = requests.get(url, timeout=10, verify=False) 

# Kiểm tra xem yêu cầu có thành công không
if response.status_code == 200:
    content = extract_text_from_pdf(response)
    sentences = split_sentences(content)
    sentences = remove_sentences(sentences)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]

    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = []
    for i, sentence in enumerate(sentences):
        print(f"Câu: {i+1}")
        print(sentence)
    for i, sentence in enumerate(all_sentences):
        try:
            embedding = embedding_vietnamese([sentence])
            embeddings.append(embedding)
        except Exception as e:
            print(f"Lỗi khi tính toán embedding cho câu: {sentence}. Lỗi: {e}")
            break
else:
    print("Không thể lấy nội dung trang web.")