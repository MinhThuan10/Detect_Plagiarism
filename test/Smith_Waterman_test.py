import numpy as np
from Bio import pairwise2
from processing_input import *

def smith_waterman(seq1, seq2, match_score=2, mismatch_penalty=-1, gap_penalty=-1):
    m, n = len(seq1), len(seq2)
    dp = np.zeros((m+1, n+1), dtype=int)
    for i in range(1, m+1):
        dp[i, 0] = gap_penalty * i
    for j in range(1, n+1):
        dp[0, j] = gap_penalty * j
    for i in range(1, m+1):
        for j in range(1, n+1):
            match = dp[i-1, j-1] + (match_score if seq1[i-1] == seq2[j-1] else mismatch_penalty)
            delete = dp[i-1, j] + gap_penalty
            insert = dp[i, j-1] + gap_penalty
            dp[i, j] = max(0, match, delete, insert)
    return dp[m, n]

sentences, search_results, all_sentence_contents, _ = search_elastic('./test/test.txt')

# Define a function to convert Smith-Waterman score to similarity ratio
def score_to_similarity(score, length1, length2):
    # Maximum possible score is length of the shorter sequence * match_score
    max_score = min(length1, length2) * 2  # assuming match_score is 2
    return score / max_score

for i, sentence in enumerate(sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in all_sentence_contents[i]]

    # Smith-Waterman calculations
    highest_score = 0
    best_result = None
    for j, reference in enumerate(preprocessed_references):
        score = smith_waterman(preprocessed_query, reference)
        similarity = score_to_similarity(score, len(preprocessed_query), len(reference))
        
        if similarity > highest_score:
            highest_score = similarity
            best_result = {
                'reference_text': all_sentence_contents[i][j],
            }
    # Tính ngưỡng động dựa trên chiều dài câu
    query_length = len(preprocessed_query.split())
    dynamic_threshold = calculate_dynamic_threshold(query_length)
    # Adjust threshold as needed (0.8 for cosine similarity)
    if highest_score >= dynamic_threshold:
        print(f"Câu {i+1}: Plagiarized content detected:")
        print("Reference:", best_result['reference_text'])
        print(f"Similarity Score: {highest_score:.2f}")
    else:
        print(f"Câu {i+1}: No plagiarism detected.")