"""MudraMitra smart search using TF-IDF and cosine similarity."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def record_to_text(record):
    """Convert MUDRA record fields into searchable text."""
    parts = []

    for key, value in record.items():
        if value:
            parts.append(key.replace("_", " "))
            parts.append(str(value).replace("_", " "))

    return " ".join(parts)


def smart_search(records, question, top_k=3):
    """Return the most relevant scheme records."""
    question = question.strip()

    if not records or not question:
        return []

    documents = [record_to_text(record) for record in records]

    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        document_matrix = vectorizer.fit_transform(documents)
        question_vector = vectorizer.transform([question])
    except ValueError:
        return []

    scores = cosine_similarity(
        question_vector,
        document_matrix
    ).flatten()

    ranked_indices = scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:
        if scores[index] > 0:
            results.append({
                **records[index],
                "score": round(float(scores[index]), 4)
            })

    return results


if __name__ == "__main__":
    from app.records import load_records

    records = load_records()

    for result in smart_search(records, "Tarun Plus eligibility"):
        print(result)
