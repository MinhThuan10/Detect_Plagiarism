from sentence_split import *
from processing import *
from connect_mongoDB import *

def processing_data(file_path):
    # Trích xuất nội dung văn bản từ file PDF với số trang
    text, total_pages, total_words = extract_pdf_text(file_path, './output/content.txt')
    # Kết hợp các dòng và tách câu, lưu cả số trang cho mỗi câu
    sentences_with_page = combine_lines_and_split_sentences(text, './output/sentence_split.txt')
    # Loại bỏ các câu có ít hơn 1 từ
    processed_sentences = remove_single_word_sentences(sentences_with_page, './output/processed_sentences.txt')
    return processed_sentences


def process_all_files_in_folder(folder_path):
    # Lấy danh sách tất cả các file trong thư mục
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    file_id_counter = 0
    for file_name in files:
        file_id_counter += 1
        # Tạo đường dẫn đầy đủ đến file
        file_path = os.path.join(folder_path, file_name)
        # Xử lý dữ liệu cho từng file
        processed_sentences = processing_data(file_path)    
        # Lưu dữ liệu vào MongoDB
        save_to_mongodb(processed_sentences, file_id_counter, file_name, 'Plagiarism', 'data')
        
if __name__ == "__main__":
    folder_path = './Data_PMT'
    process_all_files_in_folder(folder_path)



