from processing_input import *
from sentence_transformers import SentenceTransformer
import numpy as np

sentences, search_results, _, all_embeddings = search_elastic('./test/test.txt')
model = SentenceTransformer('dangvantuan/vietnamese-embedding')
def embeddind_vietnamese(text):
    embedding = model.encode(text)
    return embedding
for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    processed_sentence = embeddind_vietnamese(preprocessed_query).reshape(1, -1)
    
    # Ensure all_embeddings[i] is a numpy array
    reference_embeddings = np.array(all_embeddings[i])
    
    # Calculate cosine similarity
    similarity_scores = calculate_similarity(processed_sentence, reference_embeddings)
    # Tính ngưỡng động dựa trên chiều dài câu
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)
    # Determine plagiarized content
    plagiarism_results = []

    highest_score = 0
    best_result = None

    for j, score in enumerate(similarity_scores[0]):
        if score >= dynamic_threshold and score > highest_score:
            highest_score = score
            best_result = {
                'reference_text': search_results[i][j].get('sentence_content'),
            }

    if best_result:
        print(f"Câu thứ {i + 1}: ****Plagiarized content detected:")
        print("Reference:", best_result['reference_text'])
        print(highest_score)
    else:
        print(f"Câu thứ {i + 1}: *****No plagiarism detected.")
