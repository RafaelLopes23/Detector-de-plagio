"""Plagiarism detector package exports."""

from .compare import (
	compare_documents_tfidf,
	detect_plagiarism_tfidf,
	tfidf_cosine_similarity,
	find_similar_segments,
)
from .data_loader import load_documents, load_single_document

__all__ = [
	"load_documents",
	"load_single_document",
	"compare_documents_tfidf",
	"detect_plagiarism_tfidf",
	"tfidf_cosine_similarity",
	"find_similar_segments",
]