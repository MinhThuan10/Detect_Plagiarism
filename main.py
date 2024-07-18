from sentence_split import *
from save_txt import *
from processing import *
from feature_extraction import *
from connect_mongoDB import *

def processing_data(file_path):
    # Trích xuất nội dung văn bản từ file PDF với số trang
    text_with_page = extract_pdf_text(file_path)
    # Lưu nội dung vào file văn bản với số trang
    save_text_with_page_to_file(text_with_page, './output/content.txt')

    # Kết hợp các dòng và tách câu, lưu cả số trang cho mỗi câu
    sentences_with_page = combine_lines_and_split_sentences(text_with_page)
    # Lưu nội dung vào file văn bản với số dòng và số trang
    save_combined_text_with_page_to_file(sentences_with_page, './output/sentence_split.txt')

    # Loại bỏ các câu có ít hơn 1 từ
    processed_sentences = remove_single_word_sentences(sentences_with_page)
    # Lưu nội dung vào file văn bản
    save_combined_text_with_page_to_file(processed_sentences, './output/processed_sentences.txt')

    return processed_sentences

# def preprocess_sentences(sentences_with_page):
#     processed_sentences = []
#     all_texts = []  # Danh sách văn bản đã xử lý

#     # Tiền xử lý từng câu và thu thập vào processed_sentences
#     for sentence, page_num in sentences_with_page:
#         processed_sentence = preprocess_text_vietnamese(sentence)
#         processed_sentences.append((sentence, page_num))
#         all_texts.append(processed_sentence)

#     # Tính toán TF-IDF cho toàn bộ danh sách văn bản đã xử lý
#     features = tfidf_features(all_texts)
    
#     # Thêm features vào từng câu trong processed_sentences
#     for i, (sentence, page_num) in enumerate(sentences_with_page):
#         processed_sentences[i] = (sentence, page_num, features[i])
#     # Lưu nội dung vào file văn bản
#     save_combined_text_with_page_to_file_TFIDF(processed_sentences, './output/processed_sentences2.txt')
#     return processed_sentences


if __name__ == "__main__":
    file_path = './Data/SKL007296.pdf'
    processed_sentences = processing_data(file_path)
    # data = preprocess_sentences(processed_sentences)
    save_to_mongodb(processed_sentences, 'plagiarism', 'data')



