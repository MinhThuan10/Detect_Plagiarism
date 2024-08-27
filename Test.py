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
sentences_cache = {}

# Đường dẫn URL của file PDF
# url = 'https://www.barbercosmo.ca.gov/laws_regs/act_regs_vt.pdf'
url = 'https://www.fmu.ac.jp/home/public_h/ebm/materials/images/VN_epibook_130515_KhoaH27.4.14.pdf'
content = fetch_url(url)
sentences_cache[url] = content
print(content)
content = sentences_cache.get(url)
if content is None:
    content = fetch_url(url)
print(content)

# sentences_from_webpage = split_sentences(content)
# sentences = remove_sentences(sentences_from_webpage)


# embedding_vietnamese(sentences)
# Kết thúc và in ra thời gian thực hiện
end_time = time.time()
elapsed_time = end_time - start_time


print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
