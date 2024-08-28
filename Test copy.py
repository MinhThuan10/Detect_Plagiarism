import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
from save_txt import *
from processing import *
from concurrent.futures import ThreadPoolExecutor, as_completed

url = 'https://cait.neu.edu.vn/vi/turnitin/khai-niem-va-cac-van-de-ve-dao-van'

content = fetch_url(url)
if content:
    sentences_from_webpage = split_sentences(content)
    sentences = remove_sentences(sentences_from_webpage)
    print(sentences)