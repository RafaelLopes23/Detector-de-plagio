def load_documents(file_paths):
    documents = []
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as file:
            documents.append(file.read())
    return documents

def load_single_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()