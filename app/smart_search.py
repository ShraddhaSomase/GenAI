"""MudraMitra - smart search with TF-IDF + cosine similarity.

Ranks records against a question and returns the top matches.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def record_to_text(r):
    """Turn one record into a searchable sentence."""
    return f"{r['category']} {r['type']} {r['mode']} {r['note']} {r['date']}"


def smart_search(records, question, top_k=3):
    """Return the top_k records most similar to the question, best first.

    Each result is the record plus a 'score' between 0 and 1.
    Records with a score of 0 (no word in common) are left out.
    """
    question = question.strip()
    if not records or not question:
        return []

    docs = [record_to_text(r) for r in records]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        doc_matrix = vectorizer.fit_transform(docs)
    except ValueError:  # empty vocabulary
        return []
    q_vec = vectorizer.transform([question])

    scores = cosine_similarity(q_vec, doc_matrix).flatten()
    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)

    results = []
    for i in ranked[:top_k]:
        if scores[i] > 0:
            results.append({**records[i], "score": round(float(scores[i]), 4)})
    return results


if __name__ == "__main__":
    from app.records import load_records

    for hit in smart_search(load_records(), "how much did I spend on rent"):
        print(hit["score"], hit["category"], hit["amount"], hit["note"])