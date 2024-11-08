import re
import fitz
from transformers import RobertaTokenizer
from langdetect import detect

def is_vietnamese(text):
    try:
        # Phát hiện ngôn ngữ của văn bản
        return detect(text) == 'vi'
    except:
        # Nếu có lỗi (ví dụ: văn bản quá ngắn), trả về False
        return False
    
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
def remove_sentences(sentences):
    """
    Loại bỏ các câu có số lượng tokens vượt quá max_tokens.

    Args:
        sentences (list): Danh sách các câu cần kiểm tra.
        tokenizer (PreTrainedTokenizer): Tokenizer tương ứng với mô hình Transformer.
        max_tokens (int): Số lượng tokens tối đa cho phép. Mặc định là 512.

    Returns:
        list: Danh sách các câu sau khi lọc.
    """
    filtered_sentences = []
    for sentence in sentences:
        # Đếm số lượng tokens trong câu
        token_count = len(tokenizer.tokenize(sentence))
        # Kiểm tra điều kiện: số tokens <= 512
        if token_count < 512:
            filtered_sentences.append(sentence)
    return filtered_sentences

def split_sentences(text):
    text_with_dot = re.sub(r'(\n\s*){2,}', '. ', text)
    text_with_dot = re.sub(r'(\n)', ' ', text_with_dot)
    text = re.sub(r'\t+', ' ', text)
    text_with_dot = re.sub(r'( +)', ' ', text_with_dot)

    sentences = re.split(r'(?<=[.!?])\s+', text_with_dot)
    
    abbreviations = [
        'Tp.', 'GVHD.', 'SVTH.', 'TS.', 'KTX.', 'P.H.', 'CĐV.', 'ĐH.', 'TĐ.', 'NĐT.',
        'HĐND.', 'UBND.', 'HĐQT.', 'ĐTV.', 'TBT.', 'TT.', 'CT.', 'TCHC.', 'CSTC.', 'SĐH.',
        'TL.', 'TTXVN.', 'KQXH.', 'CNC.', 'THCS.', 'THPT.', 'TP.HCM.', 'BCĐ.', 'QH.', 'NH.'
    ]

    result = []
    for i in range(len(sentences)):
        if i > 0 and any(sentences[i - 1].strip().endswith(abbr) for abbr in abbreviations):
            result[-1] += ' ' + sentences[i].strip()
        else:
            sentence = sentences[i].strip()
            # Lọc câu không phải tiếng Việt hoặc quá ngắn
            if is_vietnamese(sentence) and len(sentence.split()) > 3:
                result.append(sentence)
    return [sentence for sentence in result if sentence]


file_path = './Data/SKL007296.pdf'
pdf_document = fitz.open(file_path)
count = 0
for i in range(pdf_document.page_count):
    page = pdf_document.load_page(i)
    text = page.get_text()
    sentences = split_sentences(text)
    sentences = remove_sentences(sentences)

    for sentence in sentences:
        count = count + 1
        print(sentence)
        print("+++++++++++++++++++++++++")

print(count)

