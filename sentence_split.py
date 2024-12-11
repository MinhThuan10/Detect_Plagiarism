import fitz
import re
from processing import model, preprocess_text_vietnamese
from pyvi.ViTokenizer import tokenize

def extract_pdf_text(pdf_path, output_file_path):
    doc = fitz.open(pdf_path)
    text = ""
    total_pages = doc.page_count  # Lấy tổng số trang
    total_words = 0
    for page in doc:
        page_text = page.get_text("text")
        text += page_text
        total_words += len(page_text.split())  # Đếm số từ trong mỗi trang
    doc.close()
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    
    return text, total_pages, total_words



def split_sentences_savefile(text, output_file_path):
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

    sentences = [clean_vietnamese_sentence(sentence) for sentence in sentences]

    with open(output_file_path, 'w', encoding='utf-8') as file:
        for i, sentence in enumerate(sentences, start=1):
            file.write(f"Câu {i}: {sentence}\n")
    

    return sentences

def clean_vietnamese_sentence(sentence):
    vietnamese_char_pattern = re.compile(
        r"[a-zA-ZĂÂÊÔƠƯÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬĐÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴăâđêôơưáàảãạắằẳẵặấầẩẫậđéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ\d\s;,:-]"
    )
    cleaned_sentence = ''.join(vietnamese_char_pattern.findall(sentence))
    cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence).strip()
    return cleaned_sentence

def remove_sentences_savefile(sentences, output_file_path):
    filtered_sentences = []
    for sentence in sentences:
        # Đếm số lượng tokens trong câu
        processed_sentences_text = preprocess_text_vietnamese(sentence)[0]
        tokenizer_sent = tokenize(processed_sentences_text)
        o = model[0].tokenizer(tokenizer_sent, return_attention_mask=False, return_token_type_ids=False)
        if len(o.input_ids) > 256:
            sentences_split = re.split(r'[;,:-]', sentence)
            sentences_split = [s.strip() for s in sentences_split if s.strip()]
            for sentence_split in sentences_split:
                processed_sentences_text_split = preprocess_text_vietnamese(sentence_split)[0]
                tokenizer_sent_split = tokenize(processed_sentences_text_split)
                o_split = model[0].tokenizer(tokenizer_sent_split, return_attention_mask=False, return_token_type_ids=False)
                if 3 < len(o_split.input_ids) <= 256 and len(sentence_split.split()) > 3:
                    filtered_sentences.append(sentence_split)
        if 3 < len(o.input_ids) <= 256  and len(sentence.split()) > 3:
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

    # sentences = re.split(r'[.!?]', text)
    sentences = re.split(r'[.!?]\s+', text)

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
        processed_sentences_text = preprocess_text_vietnamese(sentence)[0]
        tokenizer_sent = tokenize(processed_sentences_text)
        o = model[0].tokenizer(tokenizer_sent, return_attention_mask=False, return_token_type_ids=False)
        if len(o.input_ids) > 256:
            sentences_split = re.split(r'[;,:-]', sentence)
            sentences_split = [s.strip() for s in sentences_split if s.strip()]
            for sentence_split in sentences_split:
                processed_sentences_text_split = preprocess_text_vietnamese(sentence_split)[0]
                tokenizer_sent_split = tokenize(processed_sentences_text_split)
                o_split = model[0].tokenizer(tokenizer_sent_split, return_attention_mask=False, return_token_type_ids=False)
                if 3 < len(o_split.input_ids) <= 256 and len(sentence_split.split()) > 3:
                    filtered_sentences.append(sentence_split)
        if 3 < len(o.input_ids) <= 256  and len(sentence.split()) > 3:
            filtered_sentences.append(sentence)
    return filtered_sentences


