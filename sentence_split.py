import fitz
import re

def extract_pdf_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    extracted_text = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text().strip()
        if text:
            extracted_text.append((text, page_num + 1))  # page_num + 1 để đánh số trang từ 1
    pdf_document.close()
    return extracted_text


def combine_lines_and_split_sentences(text_with_page):
    combined_lines = []
    current_sentence = ''

    for text, page_num in text_with_page:
        lines = text.split('\n')
        for line in lines:
            # Loại bỏ các dòng chỉ chứa dấu chấm câu và khoảng trắng
            if re.match(r'^[\s]*$', line):
                continue
            # Xóa khoảng trắng thừa với dấu câu và loại bỏ ký tự đặc biệt và số La Mã
            line = re.sub(r'\.{2,}|\s{2,}', ' ', line)          
            
            # Tách câu nếu dòng không bắt đầu bằng số và kết hợp các dòng liên tiếp
            if line.strip():  # Only process non-empty lines
                if line[0].isupper() or line[0] in '“"':
                    if current_sentence:
                        combined_lines.append((current_sentence.strip(), page_num))
                    current_sentence = line.strip()
                else:
                    current_sentence += ' ' + line.strip()
    
    if current_sentence:
        combined_lines.append((current_sentence.strip(), page_num))
    
    return combined_lines

def remove_single_word_sentences(sentences):
    return [sentence for sentence in sentences if len(sentence[0].split()) > 2]



