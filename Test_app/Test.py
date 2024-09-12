import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from processing import *
import time
from sentence_split import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
from pymongo import MongoClient
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from urllib.parse import urlparse


preprocessed_query, sentence_results = search_sentence_elastic('facebook zalo oa youtube')

print(preprocessed_query)

print(sentence_results)