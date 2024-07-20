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

def preprocess_sentences(sentences_with_page):
    processed_sentences = []

    # Tiền xử lý từng câu và thu thập vào processed_sentences
    for sentence, _ in sentences_with_page:
        processed_sentence, _ = preprocess_text_vietnamese(sentence)
        processed_sentence = embeddind_vietnamese(processed_sentence)
        processed_sentences.append(processed_sentence)
    # Thêm features vào từng câu trong processed_sentences
    combined = [(page, original, processed) for (page, original), processed in zip(sentences_with_page, processed_sentences)]
    save_combined_text_with_page_to_file_Embedding(combined, './output/embedding_sentences.txt')
    return combined


if __name__ == "__main__":
    file_path = './Data/SKL007296.pdf'
    processed_sentences = processing_data(file_path)
    data = preprocess_sentences(processed_sentences)
    save_to_mongodb(data, 'plagiarism', 'data')



