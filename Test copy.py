import requests
import re
from sentence_split import *
# Thông tin API Key và Custom Search Engine ID
API_KEY = 'AIzaSyAe4kQFGeVqXnD0-EIx5qAUxA4aeauTx_Y'  # Thay thế bằng API Key của bạn
CX = '01d819c8b90df4a04'  # Thay thế bằng Custom Search Engine ID của bạn

def search_query(query):
    # Tạo URL truy vấn
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}"

    # Gửi yêu cầu GET tới API
    response = requests.get(url)

    # Kiểm tra xem yêu cầu có thành công không
    if response.status_code == 200:
        results = response.json()
        
        # Trích xuất và in ra các snippet từ kết quả tìm kiếm
        if 'items' in results:
            for i, item in enumerate(results['items']):
                snippet = item.get('snippet', 'No snippet available')
                print(item.get('link'))
                print(item.get('snippet'))

                sentences = split_sentences(snippet)
                for sentence in sentences:
                    print(sentence)
                print("\n")  # In dòng trắng để tách giữa các snippet
        else:
            print("No results found.")
    else:
        print(f"Error: {response.status_code}")

# Câu muốn tìm kiếm
query = "Tự đạo văn thường được hiểu là “tái sử dụng” hay “tái chế” lại các một phần hay toàn bộ nghiên cứu cũ đã được phát hành trước đó của chính bản thân"

# Thực hiện tìm kiếm
search_query(query)
