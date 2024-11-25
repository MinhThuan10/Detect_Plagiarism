import fitz
import re
from langdetect import detect
from processing import *

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

def is_vietnamese(text):
    try:
        # Phát hiện ngôn ngữ của văn bản
        return detect(text) == 'vi'
    except:
        # Nếu có lỗi (ví dụ: văn bản quá ngắn), trả về False
        return False
    

def combine_lines_and_split_sentences(text, output_file_path):
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', '', text)

    text = text.replace(' \n', '. ')
    text = text.replace('\n', ' ')
    text = re.sub(r'[ ]{2,}', ' ', text)
    text = text.replace(' .', '.')

    abbreviations = ['TS.', 'Ths.', 'THS.',  'TP.', 'Dr.', 'PhD.', 'BS.', ' Th.', 'S.']
    for abbr in abbreviations:
        text = text.replace(abbr, abbr.replace('.', '__DOT__'))

    sentences = re.split(r'[.!?]', text)
    sentences = [s.replace('__DOT__', '.') for s in sentences]
    sentences = [s.strip() for s in sentences if s.strip()]

    with open(output_file_path, 'w', encoding='utf-8') as file:
        for i, sentence in enumerate(sentences, start=1):
            file.write(f"Câu {i}: {sentence}\n")
    return sentences

def remove_single_word_sentences(sentences, output_file_path):
    filtered_sentences = []
    for sentence in sentences:
        # Đếm số lượng tokens trong câu
        o = model.tokenizer(sentence, return_attention_mask=False, return_token_type_ids=False)
        if len(o.input_ids) > 256:
            sentence_minis = re.split(r'[,:-]\s*', sentence)
            for sentence_mini in sentence_minis:
                sentence_mini = sentence_mini.strip()
                if sentence_mini:
                    o_mini = model.tokenizer(sentence, return_attention_mask=False, return_token_type_ids=False)
                    if len(o_mini.input_ids) > 256:
                        print(sentence_mini)
                        print(len(o_mini.input_ids))
                    if len(o_mini.input_ids) < 256 and len(o_mini.input_ids) > 10:
                        filtered_sentences.append(sentence_mini)
        if len(o.input_ids) < 256 and len(o.input_ids) > 10:
            filtered_sentences.append(sentence)

    with open(output_file_path, 'w', encoding='utf-8') as file:
        for i, sentence in enumerate(filtered_sentences, start=1):
            file.write(f"Câu {i}: {sentence}\n")
    return filtered_sentences



def split_sentences(text):
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', '', text)

    text = text.replace(' \n', '. ')
    text = text.replace('\n', ' ')
    text = re.sub(r'[ ]{2,}', ' ', text)
    text = text.replace(' .', '.')

    abbreviations = ['TS.', 'TP.', 'Dr.', 'PhD.', 'MSc.', 'MBA.', 'BS.', 'Prof.']
    for abbr in abbreviations:
        text = text.replace(abbr, abbr.replace('.', '__DOT__'))

    sentences = re.split(r'[.!?]', text)
    sentences = [s.replace('__DOT__', '.') for s in sentences]
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences

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
            sentences = re.split(r'[.?!]\s+', line)
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
    filtered_sentences = []
    for sentence in sentences:
        # Đếm số lượng tokens trong câu
        o = model.tokenizer(sentence, return_attention_mask=False, return_token_type_ids=False)
        if len(o.input_ids) > 256:
            sentence_minis = re.split(r'[,:-]\s*', sentence)
            for sentence_mini in sentence_minis:
                sentence_mini = sentence_mini.strip()
                if sentence_mini:
                    o_mini = model.tokenizer(sentence, return_attention_mask=False, return_token_type_ids=False)
                    if len(o_mini.input_ids) > 256:
                        print(sentence_mini)
                        print(len(o_mini.input_ids))
                    if len(o_mini.input_ids) < 256 and len(o_mini.input_ids) > 10:
                        filtered_sentences.append(sentence_mini)
        if len(o.input_ids) < 256 and len(o.input_ids) > 10:
            filtered_sentences.append(sentence)
    return filtered_sentences


