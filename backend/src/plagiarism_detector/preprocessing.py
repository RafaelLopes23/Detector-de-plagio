def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    
    # Tokenization
    tokens = text.split()
    
    return tokens

def normalize_tokens(tokens):
    # Remove stop words (example implementation)
    stop_words = set(['the', 'is', 'in', 'and', 'to', 'a'])
    normalized_tokens = [token for token in tokens if token not in stop_words]
    
    return normalized_tokens

def preprocess_document(document):
    tokens = preprocess_text(document)
    normalized_tokens = normalize_tokens(tokens)
    
    return normalized_tokens