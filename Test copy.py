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

def process_sentences(sentences, n=3):
    all_phrases = []
    for sentence in sentences:
        phrases = extract_phrases(sentence, n)
        all_phrases.extend(phrases)
    return all_phrases

# Ví dụ sử dụng
sentences = [
    "Chào bạn! Tôi là ChatGPT và tôi giúp bạn giải đáp thắc mắc.",
    "Có điều gì bạn cần biết không? Hãy cho tôi biết."
]

# Tách câu thành các cụm từ 3 từ
phrases = process_sentences(sentences, n=3)
print(phrases)
