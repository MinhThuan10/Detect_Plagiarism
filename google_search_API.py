from processing import *
import warnings
from urllib3.exceptions import InsecureRequestWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import time

# Start the timer
start_time = time.time()
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

def compare_with_combined_webpage(sentence, combined_webpage_text):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    sentences_from_webpage = combine_lines_and_split_sentences(combined_webpage_text)
    if not sentences_from_webpage:
        return 0, ""
    
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences_from_webpage]
    
    if not preprocessed_references:
        return 0, ""
    
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([preprocessed_query] + preprocessed_references)
    
    if features.shape[0] <= 1:
        return 0, ""
    
    n_components = min(100, features.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_components)
    features_lsa = svd.fit_transform(features)
    
    features_query_lsa = features_lsa[0].reshape(1, -1)
    features_references_lsa = features_lsa[1:]
    
    if features_references_lsa.shape[0] == 0:
        return 0, ""
    
    similarity_scores = calculate_similarity(features_query_lsa, features_references_lsa)
    
    if similarity_scores.shape[1] == 0:
        return 0, ""
    
    max_similarity_idx = similarity_scores.argmax()
    max_similarity = similarity_scores[0][max_similarity_idx]
    best_match = sentences_from_webpage[max_similarity_idx]
    
    return max_similarity, best_match

plagiarized_count = 0

def search_text(text):
    global plagiarized_count
    sentences = text.split('\n')
        
    for i, sentence in enumerate(sentences):
        print(f"********Tìm kiếm câu {i + 1}: {sentence}")
        result = search_google(sentence)
        items = result.get('items', [])
        
        best_match_url = None
        best_match_title = None
        best_match_similarity = 0
        best_match_sentence = ""

        for item in items:
            url = item.get('link')
            title = item.get('title')
            print(f"Checking URL: {url}")
            content = fetch_url(url)
            if content:
                similarity, match_sentence = compare_with_combined_webpage(sentence, content)        
                if similarity > best_match_similarity:
                    best_match_similarity = similarity
                    best_match_url = url
                    best_match_title = title
                    best_match_sentence = match_sentence

        # In ra thông tin của URL, tiêu đề và câu trùng khớp có độ tương đồng cao nhất
        if best_match_url:
            print(f"Max Similarity: {best_match_similarity}")
            threshold = calculate_dynamic_threshold(len(sentence.split()))
            print(f"Threshold: {threshold}")
            if best_match_similarity > threshold:
                print("+++++++Nội dung bị trùng phát hiện:")
                print(f"Title: {best_match_title}")
                print(f"URL: {best_match_url}")
                print(f"Best match sentence: {best_match_sentence}")
                plagiarized_count += 1


with open('./test/test_2.txt', 'r', encoding='utf-8') as file:
    text = file.read()

search_text(text)

# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print("Đánh giá độ hiệu quả của Google Search API ")
print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
print(f"Số lượng câu phát hiện đạo văn: {plagiarized_count}")
