
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def smart_search(question, records):

    if not records:
        return []

    documents = []

    for record in records:
        text = " ".join(
            f"{key} {value}"
            for key, value in record.items()
        )
        documents.append(text)

    all_text = documents + [question]

    vectorizer = TfidfVectorizer(stop_words="english")

    matrix = vectorizer.fit_transform(all_text)

    question_vector = matrix[-1]
    record_vectors = matrix[:-1]

    scores = cosine_similarity(
        question_vector,
        record_vectors
    ).flatten()

    top_indices = scores.argsort()[::-1][:3]

    results = []

    for index in top_indices:
        results.append({
            "record": records[index],
            "similarity_score": round(
                float(scores[index]), 4
            )
        })

    return results
