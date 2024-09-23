import fitz
import re

def extract_pdf_text(pdf_path, output_file_path):
    doc = fitz.open(pdf_path)
    text = ""
    total_pages = doc.page_count  # Lấy tổng số trang
    total_words = 0
    
    for page in doc:
        page_text = page.get_text()
        text += page_text
        total_words += len(page_text.split())  # Đếm số từ trong mỗi trang
    
    doc.close()
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    
    return text, total_pages, total_words

def combine_lines_and_split_sentences(text, output_file_path):
    processed_text = []
    combined_sentences = []
    # Bao gồm tất cả các ký tự thường trong tiếng Việt
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    
    # Thay thế '\n' theo điều kiện: Nếu có ký tự '\n' và sau đó là chữ thường tiếng Việt
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', ' ', text)
    text = re.sub(r'[^\w\s.,;?:]', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\ {2,}', ' ', text)
    text = text.replace('. ', '.\n')
    processed_text.append((text))
         
    lines = text.split('\n')
    for line in lines:
        sentences = re.split(r'[.?!]', line)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                combined_sentences.append((sentence))

    with open(output_file_path, 'w', encoding='utf-8') as file:
        for i, sentence in enumerate(combined_sentences, start=1):
            file.write(f"Câu {i}: {sentence}\n")
    return combined_sentences

def remove_single_word_sentences(sentences, output_file_path):
    sentences =  [sentence for sentence in sentences if(len(sentence.split()) > 3 and len(sentence.split()) < 100)]
    with open(output_file_path, 'w', encoding='utf-8') as file:
            for i, sentence in enumerate(sentences, start=1):
                file.write(f"Câu {i}: {sentence}\n")
    return sentences


def split_sentences(text):
    combined_sentences = []
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', '', text)
    text = text.replace('. ', '.\n')
    
    lines = text.split('\n')
    for line in lines:
        sentences = re.split(r'[.?!]', line)
        for sentence in sentences:
            sentence = sentence.strip()
            sentences = [s.strip() for s in sentences if s.strip()]
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
            sentences = re.split(r'[.?!]', line)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Tách câu thành các cụm từ
                    phrases = extract_phrases(sentence, n=2)
                    for phrase in phrases:
                        if len(phrase.split()) > 1:
                            combined_sentences.append(phrase)

    return combined_sentences


def remove_sentences(sentences):
    return [sentence for sentence in sentences if(len(sentence.split()) > 2 and len(sentence.split()) < 150)]

def remove_snippet_parts(sentences):
    return [sentence for sentence in sentences if(len(sentence.split()) > 1 and len(sentence.split()) < 100)]