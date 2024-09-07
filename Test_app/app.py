from flask import Flask, render_template
import difflib

app = Flask(__name__)

# Hai câu có sẵn
BEST_MATCH = "Đạo văn được xem là hành vi thiếu trung thực về mặt học thuật và vi phạm đạo đức báo chí."
SENTENCE = "Tuy nhiên, trong môi trường học thuật, đạo văn được coi là hành động thiếu trung thực và gây ra nhiều tranh cãi."

# Hàm tìm các từ giống nhau
def common_ordered_words_difflib(best_match, sentence):
    # Chuyển đổi văn bản thành chữ thường
    words_best_match = best_match.lower().split()
    words_sentence = sentence.lower().split()

    seq_matcher = difflib.SequenceMatcher(None, words_best_match, words_sentence)
    
    indices_best_match = []
    indices_sentence = []
    
    for match in seq_matcher.get_matching_blocks():
        if match.size > 0:
            indices_best_match.extend(range(match.a, match.a + match.size))
            indices_sentence.extend(range(match.b, match.b + match.size))

    return indices_best_match, indices_sentence

@app.route("/")
def compare():
    indices_best_match, indices_sentence = common_ordered_words_difflib(BEST_MATCH, SENTENCE)

    def highlight_text(original_text, indices):
        words = original_text.split()
        highlighted = []
        i = 0
        while i < len(words):
            if i in indices:
                # Start highlighting
                start = i
                while i in indices and i < len(words):
                    i += 1
                # Include space if the next word is also in the indices
                highlighted.append(f'<span class="highlight">{" ".join(words[start:i])}</span>')
            else:
                highlighted.append(words[i])
                i += 1
        return " ".join(highlighted)

    # Tạo các câu đã được highlight
    highlighted_best_match = highlight_text(BEST_MATCH, indices_best_match)
    highlighted_sentence = highlight_text(SENTENCE, indices_sentence)
    
    return render_template("index.html", 
        highlighted_best_match=highlighted_best_match, 
        highlighted_sentence=highlighted_sentence
    )

if __name__ == "__main__":
    app.run(debug=True)
