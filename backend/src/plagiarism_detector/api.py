from flask import Flask, jsonify, request
import os

from plagiarism_detector.compare import (
    compare_documents_tfidf,
    detect_plagiarism_tfidf,
    find_similar_segments,
    find_similar_passages,
    explain_tfidf_similarity,
)

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(
        {
            "service": "Plagiarism Detector API",                                                                                                                        
            "version": "1.0",
            "endpoints": {                                                                                                                                                                                                              
                "compare": "/api/compare (POST)",
                "health": "/health (GET)"
            }
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.post("/api/compare")
def compare_endpoint():
    payload = request.get_json(force=True, silent=False) or {}
    text_a = payload.get("text_a", "")
    text_b = payload.get("text_b", "")
    analyzer = (payload.get("analyzer") or "word").lower()
    # ngram_range can be like [3,5] or "3,5" -> normalize
    ngram_val = payload.get("ngram_range")
    if isinstance(ngram_val, (list, tuple)) and len(ngram_val) == 2:
        ngram_range = (int(ngram_val[0]), int(ngram_val[1]))
    elif isinstance(ngram_val, str) and "," in ngram_val:
        a, b = ngram_val.split(",", 1)
        ngram_range = (int(a), int(b))
    else:
        ngram_range = (1, 2)

    # Choose TF-IDF parameters based on analyzer
    if analyzer not in ("char", "word"):
        analyzer = "char"
    from plagiarism_detector.compare import tfidf_cosine_similarity

    similarity = tfidf_cosine_similarity(
        text_a, text_b, analyzer=analyzer, ngram_range=ngram_range
    )
    is_plagiarism = similarity >= 0.5
    # For matches, align analyzer: word-based matches if analyzer == word
    matches = find_similar_segments(text_a, text_b, analyzer=analyzer)
    passages = find_similar_passages(
        text_a, text_b, analyzer=analyzer, ngram_range=ngram_range, min_sim=0.35, top_k=5
    )
    explanations = explain_tfidf_similarity(
        text_a, text_b, analyzer=analyzer, ngram_range=ngram_range, top_k=10
    )

    return jsonify(
        {
            "similarity": similarity,
            "is_plagiarism": is_plagiarism,
            "threshold": 0.5,
            "matches": matches,
            "method": "tfidf",
            "analyzer": analyzer,
            "ngram_range": list(ngram_range),
            "passages": passages,
            "explanations": explanations,
        }
    )


def create_app():
    return app


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
    app.run(host=host, port=port, debug=debug)
