import difflib
import re

def common_ordered_words_difflib(best_match, sentence):
    # Tách từ và ký tự đặc biệt nhưng bỏ qua khoảng trắng thừa
    def clean_text(text):
        # Tách chuỗi thành các từ hoặc ký tự đặc biệt riêng lẻ
        return re.findall(r'\w+|[^\w\s]', text)

    # Chuẩn hóa văn bản cho cả hai chuỗi
    words_best_match = clean_text(best_match)
    words_sentence = clean_text(sentence)

    # SequenceMatcher để so sánh 2 chuỗi không phân biệt chữ hoa chữ thường
    seq_matcher = difflib.SequenceMatcher(None, [w.lower() for w in words_best_match], [w.lower() for w in words_sentence])

    common_words = []
    indices_best_match = []
    paragraphs = []  # Mảng chứa các cụm từ trùng khớp (paragraphs)
    current_paragraph = []
    word_count_sml = 0  # Biến đếm số từ trùng khớp

    def is_word(token):
        return re.match(r'\w+', token)

    # Lặp qua các khối matching
    for match in seq_matcher.get_matching_blocks():
        if match.size > 0:  # Nếu có từ hoặc ký tự giống nhau
            matched_words_best_match = words_best_match[match.a: match.a + match.size]
            matched_words_sentence = words_sentence[match.b: match.b + match.size]  # Trích từ `sentence`

            # Nếu đoạn trùng khớp liên tiếp, thêm vào current_paragraph
            if len(current_paragraph) > 0 and match.b == indices_best_match[-1] + 1:
                current_paragraph.extend(matched_words_sentence)  # Lấy từ `sentence`
            else:
                # Nếu không liên tiếp, kết thúc đoạn hiện tại và bắt đầu đoạn mới
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))  # Nối lại với khoảng trắng
                current_paragraph = matched_words_sentence  # Bắt đầu đoạn mới từ `sentence`

            # Cập nhật chỉ số và đếm số từ cho đoạn trùng khớp
            indices_best_match.extend(range(match.b, match.b + match.size))
            for word in matched_words_best_match:
                if is_word(word):  # Chỉ đếm từ thực sự
                    word_count_sml += 1

            # Thêm các từ trùng khớp vào danh sách từ trùng khớp
            common_words.extend(matched_words_best_match)

    # Thêm đoạn cuối cùng vào paragraphs nếu có
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    # Đảm bảo khoảng trắng không cần thiết không xuất hiện
    paragraphs = [para.replace(' .', '.').replace(' ,', ',') for para in paragraphs]

    return word_count_sml, indices_best_match, paragraphs

# Đoạn test
best_match = 'ĐỘ TIN CẬY CRONBACH’S ALPHA, TỈ LỆ PHẦN TRĂM, GIÁ TRỊ TRUNG BÌNH, ĐỘ'
sentence = 'ĐỘ TIN CẬY CRONBACH’S ALPHA, TỈ LỆ PHẦN TRĂM, GIÁ TRỊ TRUNG BÌNH'
word_count_sml, indices_best_match, paragraphs = common_ordered_words_difflib(best_match, sentence)

print(word_count_sml)
print(indices_best_match)
print(paragraphs)
