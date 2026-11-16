"""MudraMitra smart search using TF-IDF and cosine similarity."""

import json

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


def remove_duplicates(records):
    """Remove exact duplicate records while preserving order."""
    unique_records = []
    seen = set()

    for record in records:
        record_key = json.dumps(
            record,
            sort_keys=True,
            ensure_ascii=False
        )

        if record_key not in seen:
            seen.add(record_key)
            unique_records.append(record)

    return unique_records


def smart_search(records, question, top_k=3, diversify_categories=False):
    """Return relevant unique records, optionally prioritizing categories."""
    question = question.strip()

    if not records or not question:
        return []

    # Expand common business-related questions with MUDRA terms.
    expanded_question = question
    business_terms = (
        "business",
        "businesses",
        "business type",
        "business activity",
        "business activities",
    )

    if any(term in question.lower() for term in business_terms):
        expanded_question += (
            " manufacturing processing trading service sector "
            "non-farm income generating activity"
        )

    records = remove_duplicates(records)
    documents = [record_to_text(record) for record in records]

    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        document_matrix = vectorizer.fit_transform(documents)
        question_vector = vectorizer.transform([expanded_question])
    except ValueError:
        return []

    scores = cosine_similarity(
        question_vector,
        document_matrix
    ).flatten()

    ranked_indices = scores.argsort()[::-1]
    selected_indices = []

    if diversify_categories:
        seen_categories = set()

        # First, select the best matching record from each category
        for index in ranked_indices:
            if scores[index] <= 0:
                continue

            category = records[index].get("loan_category", "Unknown")

            if category not in seen_categories:
                selected_indices.append(index)
                seen_categories.add(category)

            if len(selected_indices) >= top_k:
                break

    # Fill remaining places with other relevant records
    for index in ranked_indices:
        if scores[index] <= 0:
            continue

        if index not in selected_indices:
            selected_indices.append(index)

        if len(selected_indices) >= top_k:
            break

    return [
        {
            **records[index],
            "score": round(float(scores[index]), 4)
        }
        for index in selected_indices
    ]


if __name__ == "__main__":
    from app.records import load_records

    records = load_records()

    results = smart_search(
        records,
        "MUDRA loan categories and loan limits Shishu Kishor Tarun Tarun Plus",
        top_k=5,
        diversify_categories=True
    )

    for result in results:
        print(result)
