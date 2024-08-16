from sentence_split import *
from save_txt import *
from processing import *
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
    
    # Tiền xử lý từng câu
    for sentence, _ in sentences_with_page:
        processed_sentence, _ = preprocess_text_vietnamese(sentence)
        processed_sentences.append(processed_sentence)
    # Thực hiện embedding cho tất cả các câu đã xử lý
    embeddings = embedding_vietnamese(processed_sentences)
    # Kết hợp features vào từng câu trong processed_sentences
    combined = [(page, original, embedding) for (page, original), embedding in zip(sentences_with_page, embeddings)]
    save_combined_text_with_page_to_file_Embedding(combined, './output/embedding_sentences.txt')
    return combined

def process_all_files_in_folder(folder_path):
    # Lấy danh sách tất cả các file trong thư mục
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

    for file_name in files:
        # Tạo đường dẫn đầy đủ đến file
        file_path = os.path.join(folder_path, file_name)
        
        # Xử lý dữ liệu cho từng file
        processed_sentences = processing_data(file_path)
        data = preprocess_sentences(processed_sentences)
        
        # Lưu dữ liệu vào MongoDB
        save_to_mongodb(data, file_name, 'Plagiarism_Embedding', 'data')
        
if __name__ == "__main__":
    folder_path = './Data'
    process_all_files_in_folder(folder_path)



