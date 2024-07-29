from processing_input import *
from sklearn.decomposition import TruncatedSVD

sentences, search_results, all_sentence_contents, _ = search_elastic('./test/test.txt')

for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]
    
    # Tính toán TF-IDF cho câu query và các câu tham chiếu
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([preprocessed_query] + preprocessed_references)
    
    # Áp dụng TruncatedSVD để thực hiện LSA
    svd = TruncatedSVD(n_components=100)  # n_components là số lượng thành phần giữ lại sau SVD
    features_lsa = svd.fit_transform(features)
    
    features_query_lsa = features_lsa[0].reshape(1, -1)
    features_references_lsa = features_lsa[1:]

    # Tính độ tương đồng cosine
    similarity_scores = calculate_similarity(features_query_lsa, features_references_lsa)

    # Xác định nội dung có sao chép
    plagiarism_results = []

    highest_score = 0
    best_result = None

    for j, score in enumerate(similarity_scores[0]):
        if score >= 0.8 and score > highest_score:
            highest_score = score
            best_result = {
                'reference_text': all_sentence_contents[i][j],
            }

    if best_result:
        print(f"Câu thứ {i + 1}: ****Plagiarized content detected:")
        print("Reference:", best_result['reference_text'])
        print(highest_score)
    else:
        print(f"Câu thứ {i + 1}: ****No plagiarism detected.")

