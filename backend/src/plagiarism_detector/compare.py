from typing import List, Dict, Tuple
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
try:
    from nltk.stem import PorterStemmer
except Exception:  # pragma: no cover - fallback if nltk not available
    PorterStemmer = None


def find_similar_segments(
    text_a: str,
    text_b: str,
    *,
    analyzer: str = "char",
    min_length: int = 20,
    max_matches: int = 5,
) -> List[Dict]:
    """
    Return up to max_matches similar segments between text_a and text_b.

    - analyzer: 'char' (default) usa comparação por caracteres; 'word' compara por tokens.
    - min_length: mínimo de caracteres (char) ou de tokens (word) por segmento.

    Cada item contém: a_start, b_start, length (chars se 'char', tokens se 'word'),
    a_snippet, b_snippet.
    """
    if analyzer == "word":
        # Tokenize preserving offsets
        def tokenize_with_spans(s: str) -> Tuple[List[str], List[Tuple[int, int]]]:
            tokens: List[str] = []
            spans: List[Tuple[int, int]] = []
            start = None
            for i, ch in enumerate(s):
                if not ch.isspace() and start is None:
                    start = i
                if ch.isspace() and start is not None:
                    tokens.append(s[start:i])
                    spans.append((start, i))
                    start = None
            if start is not None:
                tokens.append(s[start:])
                spans.append((start, len(s)))
            return tokens, spans

        tokens_a, spans_a = tokenize_with_spans(text_a)
        tokens_b, spans_b = tokenize_with_spans(text_b)

        matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b, autojunk=True)
        blocks = matcher.get_matching_blocks()
        filtered = [b for b in blocks if b.size >= max(1, min_length)]
        filtered.sort(key=lambda b: b.size, reverse=True)
        results: List[Dict] = []
        for b in filtered[:max_matches]:
            # Map token indices to char spans
            a_start_char = spans_a[b.a][0] if b.size > 0 else 0
            a_end_char = spans_a[b.a + b.size - 1][1] if b.size > 0 else 0
            b_start_char = spans_b[b.b][0] if b.size > 0 else 0
            b_end_char = spans_b[b.b + b.size - 1][1] if b.size > 0 else 0
            results.append(
                {
                    "a_start": a_start_char,
                    "b_start": b_start_char,
                    "length": b.size,
                    "a_snippet": text_a[a_start_char:a_end_char],
                    "b_snippet": text_b[b_start_char:b_end_char],
                }
            )
        return results

    # Default: character-based matches
    matcher = difflib.SequenceMatcher(None, text_a, text_b, autojunk=True)
    blocks = matcher.get_matching_blocks()
    filtered = [b for b in blocks if b.size >= max(1, min_length)]
    filtered.sort(key=lambda b: b.size, reverse=True)
    results: List[Dict] = []
    for b in filtered[:max_matches]:
        a_snip = text_a[b.a : b.a + b.size]
        b_snip = text_b[b.b : b.b + b.size]
        results.append(
            {
                "a_start": b.a,
                "b_start": b.b,
                "length": b.size,
                "a_snippet": a_snip,
                "b_snippet": b_snip,
            }
        )
    return results


# ---- TF-IDF Cosine Similarity (advanced) ----

def tfidf_cosine_similarity(
    text_a: str,
    text_b: str,
    *,
    analyzer: str = "word",
    ngram_range=(1, 2),
    min_df: int = 1,
    max_features: int | None = None,
) -> float:
    """Return cosine similarity between TF-IDF vectors of two texts.

    - analyzer: 'word' or 'char' (char n-grams often capture reordenações e variações leves)
    - ngram_range: tuple como (1,2) para uni+bi-gramas
    """
    # Guardas para entradas vazias evitarem vocabulário vazio do TF-IDF
    if not (text_a or "").strip() and not (text_b or "").strip():
        return 1.0
    if not (text_a or "").strip() or not (text_b or "").strip():
        return 0.0
    vect = TfidfVectorizer(
        analyzer=analyzer,
        ngram_range=ngram_range,
        min_df=min_df,
        max_features=max_features,
        lowercase=True,
    )
    try:
        X = vect.fit_transform([text_a, text_b])
        sim = cosine_similarity(X[0], X[1])[0, 0]
        return float(sim)
    except ValueError:
        # Ex.: vocabulário vazio após filtragem
        return 0.0


def compare_documents_tfidf(text_a: str, text_b: str) -> float:
    """Default advanced similarity: char 3-5 grams TF-IDF + cosine."""
    return tfidf_cosine_similarity(text_a, text_b, analyzer="char", ngram_range=(3, 5))


def detect_plagiarism_tfidf(text_a: str, text_b: str, threshold: float = 0.5) -> bool:
    return compare_documents_tfidf(text_a, text_b) >= threshold


# ---- Explanations and higher-level alignment ----

def _split_sentences(text: str) -> List[str]:
    # Naive sentence splitter: split by . ! ? ; : and newlines, keep reasonable chunks
    parts = re.split(r"(?<=[\.!?;:])\s+|\n+", text.strip())
    # Filter out empties and very short fragments
    return [p.strip() for p in parts if p and len(p.strip()) > 10]


def _normalize_for_compare(s: str) -> str:
    # Lowercase, remove punctuation and collapse whitespace
    s = s.lower()
    s = re.sub(r"[\W_]+", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _is_sentence_like(s: str, min_chars: int = 30, min_words: int = 8) -> bool:
    if len(s) < min_chars:
        return False
    words = re.findall(r"\b\w+\b", s)
    if len(words) < min_words:
        return False
    # Heuristic: avoid code-like lines with lots of symbols or many short tokens
    punct_ratio = len(re.findall(r"[^\w\s]", s)) / max(1, len(s))
    if punct_ratio > 0.35:
        return False
    return True


def _near_identical(a: str, b: str, threshold: float = 0.995) -> bool:
    na = _normalize_for_compare(a)
    nb = _normalize_for_compare(b)
    if na == nb:
        return True
    ratio = difflib.SequenceMatcher(None, na, nb, autojunk=True).ratio()
    return ratio >= threshold


def find_similar_passages(
    text_a: str,
    text_b: str,
    *,
    analyzer: str = "word",
    ngram_range: Tuple[int, int] = (1, 2),
    min_sim: float = 0.5,
    top_k: int = 5,
) -> List[Dict]:
    """Find pairs of similar sentences/passages across A and B using TF-IDF + cosine.

    Returns list of { a_sentence, b_sentence, similarity } sorted by sim desc.
    """
    sents_a_all = _split_sentences(text_a)
    sents_b_all = _split_sentences(text_b)
    # Keep only sentence-like content to avoid trivial names/citations/code lines
    idx_a = [i for i, s in enumerate(sents_a_all) if _is_sentence_like(s)]
    idx_b = [j for j, s in enumerate(sents_b_all) if _is_sentence_like(s)]
    sents_a = [sents_a_all[i] for i in idx_a]
    sents_b = [sents_b_all[j] for j in idx_b]
    if not sents_a or not sents_b:
        return []
    # Vectorizer 1: as requested (word/char)
    vect_main = TfidfVectorizer(analyzer=analyzer, ngram_range=ngram_range, lowercase=True)
    corpus_main = sents_a + sents_b
    try:
        X_main = vect_main.fit_transform(corpus_main)
    except ValueError:
        return []
    XA_main = X_main[: len(sents_a)]
    XB_main = X_main[len(sents_a) :]
    S_main = cosine_similarity(XA_main, XB_main)

    # Vectorizer 2: stemming-based (helps catch paraphrases with word variants)
    def _tokenize_stem(text: str):
        tokens = re.findall(r"\b\w+\b", text.lower())
        if PorterStemmer is None:
            return tokens
        stemmer = PorterStemmer()
        return [stemmer.stem(t) for t in tokens]

    vect_stem = TfidfVectorizer(analyzer='word', tokenizer=_tokenize_stem, lowercase=True)
    corpus_stem = sents_a + sents_b
    try:
        X_stem = vect_stem.fit_transform(corpus_stem)
        XA_stem = X_stem[: len(sents_a)]
        XB_stem = X_stem[len(sents_a) :]
        S_stem = cosine_similarity(XA_stem, XB_stem)
    except Exception:
        # If anything goes wrong, fall back to main similarity only
        S_stem = None

    # Combine similarities, preferring higher score across models
    if S_stem is not None and S_stem.shape == S_main.shape:
        S = np.maximum(S_main, S_stem)
    else:
        S = S_main
    pairs: List[Tuple[int, int, float]] = []
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            sim = float(S[i, j])
            if sim >= min_sim:
                # Skip exact or near-identical sentences; we want paraphrases
                if _near_identical(sents_a[i], sents_b[j]):
                    continue
                pairs.append((i, j, sim))
    pairs.sort(key=lambda t: t[2], reverse=True)
    results: List[Dict] = []
    used_a = set()
    used_b = set()
    for i, j, sim in pairs:
        if i in used_a or j in used_b:
            continue
        results.append({"a_sentence": sents_a[i], "b_sentence": sents_b[j], "similarity": sim})
        used_a.add(i)
        used_b.add(j)
        if len(results) >= top_k:
            break
    return results


def explain_tfidf_similarity(
    text_a: str,
    text_b: str,
    *,
    analyzer: str = "word",
    ngram_range: Tuple[int, int] = (1, 2),
    top_k: int = 10,
) -> List[Dict]:
    """Return top contributing n-grams (feature-level) to the cosine similarity.

    We compute TF-IDF for both docs, take element-wise product as a simple
    contribution proxy, and return top-k features present in ambos.
    """
    vect = TfidfVectorizer(analyzer=analyzer, ngram_range=ngram_range, lowercase=True)
    try:
        X = vect.fit_transform([text_a, text_b]).toarray()
    except ValueError:
        return []
    fa = X[0]
    fb = X[1]
    contrib = fa * fb  # proxy for shared weight
    if not np.any(contrib):
        return []
    idxs = np.argsort(contrib)[::-1]
    feats = vect.get_feature_names_out()
    results: List[Dict] = []
    for idx in idxs[:top_k]:
        if contrib[idx] <= 0:
            break
        results.append(
            {
                "feature": str(feats[idx]),
                "weight_a": float(fa[idx]),
                "weight_b": float(fb[idx]),
                "contribution": float(contrib[idx]),
            }
        )
    return results