import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from processing import *
from sentence_split import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

best_match = 'Vì vậy, việc sử dụng lại một phần nghiên cứu mà không trích dẫn hay có sự cho phép của nhà xuất bản là không được chấp nhận'

sentence = 'Do đó, việc sử dụng lại một phần nghiên cứu mà không trích dẫn hoặc không có sự cho phép của nhà xuất bản là không được chấp nhận'


word_count_sml, indices_best_match, c, d, e =  common_ordered_words_difflib(best_match, sentence)

print(word_count_sml)
print(indices_best_match)
print(c)
print(d)

print(e)
