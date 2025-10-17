import argparse
from plagiarism_detector import compare, data_loader

def main():
    parser = argparse.ArgumentParser(description="Plagiarism Detector CLI")
    parser.add_argument('file1', type=str, help='Path to the first document to compare')
    parser.add_argument('file2', type=str, help='Path to the second document to compare')

    args = parser.parse_args()

    # Load documents
    doc1 = data_loader.load_single_document(args.file1)
    doc2 = data_loader.load_single_document(args.file2)

    # Compare documents
    similarity_score = compare.compare_documents(doc1, doc2)
    is_plagiarism = compare.detect_plagiarism(doc1, doc2)

    print(f"Similarity between '{args.file1}' and '{args.file2}': {similarity_score:.2%}")
    print(f"Plagiarism detected: {'Yes' if is_plagiarism else 'No'}")

if __name__ == "__main__":
    main()