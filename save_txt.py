def save_text_with_page_to_file(lines_with_page, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for line, page_num in lines_with_page:
            file.write(f"Số trang {page_num}:\n{line}\n\n")

def save_combined_text_with_page_to_file(combined_text_with_page, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for i, (sentence, page_num) in enumerate(combined_text_with_page, start=1):
            file.write(f"Trang {page_num}, Câu {i}: {sentence}\n")

def save_combined_text_with_page_to_file_TFIDF(combined_text_with_page, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for i, (sentence, page_num, feature_query) in enumerate(combined_text_with_page, start=1):
            file.write(f"Trang {page_num}, Câu {i}: {sentence}\nGiá trị TF-IDF:\n {feature_query}\n")