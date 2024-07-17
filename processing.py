import spacy

# Load Vietnamese spaCy model
nlp = spacy.blank("vi")

def preprocess_text_vietnamese(text):
    # Process text with spaCy pipeline
    doc = nlp(text)

    # Filter out stopwords and punctuation, and convert to lowercase
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]

    # Join tokens back into a single string
    processed_text = ' '.join(tokens)

    return processed_text
