import difflib

def common_ordered_words_difflib(best_match, sentence):
    # Tách câu thành danh sách từ
    words_best_match = best_match.lower().split()
    words_sentence = sentence.lower().split()

    # Sử dụng difflib để tìm các từ giống nhau theo thứ tự
    seq_matcher = difflib.SequenceMatcher(None, words_best_match, words_sentence)
    
    common_words = []
    indices_best_match = []
    indices_sentence = []
    
    # Lấy các đoạn (matching blocks) giống nhau
    for match in seq_matcher.get_matching_blocks():
        if match.size > 0:  # Nếu có từ giống nhau
            common_words.extend(words_best_match[match.a: match.a + match.size])
            indices_best_match.extend(range(match.a, match.a + match.size))
            indices_sentence.extend(range(match.b, match.b + match.size))

    # Trả về số từ giống nhau (độ dài của danh sách common_words) và vị trí các từ
    return len(common_words), indices_best_match, indices_sentence

# Câu 1 và câu 2
best_match = "Đạo văn được xem là hành vi thiếu trung thực về mặt học thuật và vi phạm đạo đức báo chí."
sentence = "Tuy nhiên, trong môi trường học thuật, đạo văn được coi là hành động thiếu trung thực và gây ra nhiều tranh cãi."

# Tính các từ giống nhau theo thứ tự và in ra kết quả
word_count_sml, indices_best_match, indices_sentence = common_ordered_words_difflib(best_match, sentence)

print(f"Các từ giống nhau theo thứ tự: {word_count_sml}")
print(f"Vị trí các từ trong câu 1: {indices_best_match}")
print(f"Vị trí các từ trong câu 2: {indices_sentence}")
