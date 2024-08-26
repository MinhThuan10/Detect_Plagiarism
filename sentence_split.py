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

def combine_lines_and_split_sentences(extracted_text):
    processed_text = []
    combined_sentences = []
    # Bao gồm tất cả các ký tự thường trong tiếng Việt
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    
    for text, page_num in extracted_text:
        # Thay thế '\n' theo điều kiện: Nếu có ký tự '\n' và sau đó là chữ thường tiếng Việt
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', ' ', text)
        text = re.sub(r'[^\w\s.,;?:]', ' ', text)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\ {2,}', ' ', text)
        text = text.replace('. ', '.\n')
        processed_text.append((text, page_num))
         
    for text, page_num in processed_text:
        lines = text.split('\n')
        for line in lines:
            sentences = re.split(r'[.?!:;]', line)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    combined_sentences.append((sentence, page_num))

    return combined_sentences

def remove_single_word_sentences(sentences):
    return [sentence for sentence in sentences if(len(sentence[0].split()) > 3 and len(sentence[0].split()) < 100)]


def split_sentences(text):
    combined_sentences = []
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', ' ', text)
    text = re.sub(r'[^\w\s.,;?:!]', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\ {2,}', ' ', text)
    text = text.replace('. ', '.\n')
    
    lines = text.split('\n')
    for line in lines:
        sentences = re.split(r'[.?!:;]', line)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                combined_sentences.append(sentence)

    return combined_sentences

def extract_phrases(sentence, n=3):
    # Tách câu thành các từ
    words = sentence.split()
    # Danh sách để lưu các cụm từ
    phrases = []
    
    # Nếu số từ ít hơn n, không thể tạo cụm từ
    if len(words) < n:
        return phrases
    
    # Tạo các cụm từ với khoảng n từ
    for i in range(0, len(words), n):
        phrase = ' '.join(words[i:i + n])
        phrases.append(phrase)
    
    return phrases

def split_snippet(text):
    combined_sentences = []
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', ' ', text)
    text = re.sub(r'[^\w\s.,;?:!]', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\ {2,}', ' ', text)
    text = re.sub(r' \r', '', text)
    text = text.replace('. ', '.\n')
    
    lines = text.split('\n')
    for line in lines:
            sentences = re.split(r'[.?!:;]', line)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Tách câu thành các cụm từ
                    phrases = extract_phrases(sentence, n=3)
                    combined_sentences.extend(phrases)

    return combined_sentences


def remove_sentences(sentences):
    return [sentence for sentence in sentences if(len(sentence.split()) > 3 and len(sentence.split()) < 100)]

def remove_snippet_parts(sentences):
    return [sentence for sentence in sentences if(len(sentence.split()) > 1 and len(sentence.split()) < 100)]