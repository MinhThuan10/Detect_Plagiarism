from sentence_split import *
from processing import *
from connect_mongoDB import *
import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

def processing_data(file_path):
    # Trích xuất nội dung văn bản từ file PDF với số trang
    text, total_pages, total_words = extract_pdf_text(file_path, './output/content.txt')
    # Kết hợp các dòng và tách câu, lưu cả số trang cho mỗi câu

    sentences_with_page = split_sentences_savefile(text, './output/sentence_split.txt')
    # Loại bỏ các câu có ít hơn 1 từ
    
    processed_sentences = remove_sentences_savefile(sentences_with_page, './output/processed_sentences.txt')
    return processed_sentences

ip_cluster = 'http://localhost:9200'
school_id = '1'
school_name = 'Ho Chi Minh City University of Technology and Education'
index_name = 'plagiarism_vector'
type = 'Ấn bản'
es = Elasticsearch([ip_cluster], request_timeout=1000)
def process_all_files_in_folder(folder_path):
    # Lấy danh sách tất cả các file trong thư mục
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    file_id_counter = 0
    for file_name in files:
        file_id_counter -= 1
        # Tạo đường dẫn đầy đủ đến file
        file_path = os.path.join(folder_path, file_name)
        # Xử lý dữ liệu cho từng file
        processed_sentences = processing_data(file_path) 
        print(file_name, file_id_counter)
        processed_sentences_text = [preprocess_text_vietnamese(sentence)[0] for sentence in processed_sentences]   
        if processed_sentences_text:
            vectors = embedding_vietnamese(processed_sentences_text)
            # Lưu dữ liệu vào MongoDB
            # save_to_mongodb(processed_sentences, file_id_counter, file_name, 'Plagiarism', 'data')
            
            # save_to_elasticsearch(ip_cluster, processed_sentences,school_id, school_name, file_id_counter, file_name, index_name, type)
            save_to_elasticsearch(es, processed_sentences, vectors, school_id, school_name, file_id_counter, file_name, index_name, type)

        
if __name__ == "__main__":
    folder_path = 'G:\\data_lib\\DO AN TOT NGHIEP'
    # folder_path = './Data'

    process_all_files_in_folder(folder_path)



    # file_path = 'G:\\data_lib\\DO AN TOT NGHIEP\\SKL003086.pdf'
    # processed_sentences = processing_data(file_path) 
    # tokenizer = model.tokenizer

    # processed_sentences_text = [preprocess_text_vietnamese(sentence)[0] for sentence in processed_sentences]   
    # for i, sentence in enumerate(processed_sentences_text):
    #     print(sentence)
    #     tokens = tokenizer.tokenize(sentence)
    #     print(len(tokens))
    #     vectors = embedding_vietnamese(sentence)
        # Lưu dữ liệu vào MongoDB

    # tokenizer = model.tokenizer
    # sentence = "Documents and SettingsAdminDesktopDO AN 127hoiDO AN TOT NGHIEPmach inSO DO NGUY VCC DOUT OSC2 OSC1 TE D0 D1 D2 D3 A0 A1 A2 A3 A4 A5 A6 A7 VSS A1 A2 A0 A3 A4 A5 A6 A7 VSS VCC VT OSC2 OSC1 DIN D0 D1 D2 D3 VCC A0 A2 A3 A4 A5 A6 A7 VSS D3 D2 D1 D0 DIN OSC1 OSC2 VT A1 VT VCC A2 A3 A4 A5 A6 A7 VSS D3 D2 D1 D0 DIN OSC1 OSC2 A0 A1 VSS A7 A6 A5 A4 A3 A2 A1 A0 VCC VT OSC2 OSC1 DIN D0 D1 D2 D3 A2 A0 A1 A3 A4 A5 A6 A7 VSS VCC VT OSC2 OSC1 DIN D0 D1 D2 D3 AT89S51"
    # vectors = embedding_vietnamese(sentence)
    # sentences_with_page = remove_sentences_savefile(sentence, './output/processed_sentences.txt')
    # print(sentences_with_page)