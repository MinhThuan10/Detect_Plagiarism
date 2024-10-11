
import json
import sys
import os
# Thêm đường dẫn của thư mục cha vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from processing import *

embedding = 'Mô hình đa nh lửa lại sử dụng 6 bobine trong đó có 5 bobine điện cảm và 1 bobine điện dung, tương ư ng 5 lần đa nh lửa điện cảm sẽ có 1 lần đa nh lửa điện dung.'

query_embedding = embedding_vietnamese(embedding)

# Create a dictionary with the text_data
json_data = {"text": embedding, "embedding": query_embedding.tolist()}

# Convert the dictionary to a JSON-formatted string
json_string = json.dumps(json_data, indent=2)

# Print the JSON string
print(json_string)