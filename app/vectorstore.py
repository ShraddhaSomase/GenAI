"""Store and search document embeddings using ChromaDB."""

from pathlib import Path

import chromadb

from app.chunking import load_documents
from app.embed import embed_texts

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "mudramitra_documents"


def get_collection():
    """Create or connect to the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=str(DB_PATH))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def index_documents():
    """Generate embeddings and save document chunks in ChromaDB."""
    documents = load_documents()

    if not documents:
        print("No documents found.")
        return 0

    texts = [item["text"] for item in documents]
    embeddings = embed_texts(texts)

    collection = get_collection()

    collection.upsert(
        ids=[item["id"] for item in documents],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": item["source"],
                "page": item["page"],
                "title": item["title"]
            }
            for item in documents
        ]
    )

    print("Indexing completed!")
    print("Total documents stored:", collection.count())

    return collection.count()


def semantic_search(query, n_results=5):
    """Find document chunks related to the user's question."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_texts([query])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    hits = []

    for i in range(len(results["ids"][0])):
        hits.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "page": results["metadatas"][0][i]["page"],
            "title": results["metadatas"][0][i]["title"],
            "distance": results["distances"][0][i]
        })

    return hits


if __name__ == "__main__":
    index_documents()



def hybrid_search(query, n_results=5):
    """Combine semantic and keyword search using reciprocal rank fusion."""

    import re

    collection = get_collection()

    if collection.count() == 0:
        return []

    # 1. Get semantic search results
    semantic_hits = semantic_search(
        query,
        n_results=min(n_results * 3, collection.count())
    )

    # 2. Get all indexed documents for keyword matching
    stored = collection.get(
        include=["documents", "metadatas"]
    )

    stop_words = {
        "what", "are", "is", "the", "a", "an", "to",
        "under", "for", "of", "in", "on", "and",
        "does", "do", "can", "how", "who", "which"
    }

    query_terms = {
        word for word in re.findall(r"\b[a-zA-Z]+\b", query.lower())
        if len(word) > 2 and word not in stop_words
    }

    # MUDRA and PMMY refer to the same scheme.
    if "mudra" in query_terms:
        query_terms.add("pmmy")

    if "pmmy" in query_terms:
        query_terms.add("mudra")

    keyword_hits = []

    for i, document in enumerate(stored["documents"]):
        document_terms = set(
            re.findall(r"\b[a-zA-Z]+\b", document.lower())
        )

        matched_terms = query_terms.intersection(document_terms)

        if matched_terms:
            keyword_hits.append({
                "id": stored["ids"][i],
                "text": document,
                "source": stored["metadatas"][i]["source"],
                "page": stored["metadatas"][i]["page"],
                "title": stored["metadatas"][i]["title"],
                "distance": None,
                "matched_terms": len(matched_terms)
            })

    # 3. Rank keyword results by number of matching terms
    keyword_hits.sort(
        key=lambda item: item["matched_terms"],
        reverse=True
    )

    # Give stronger preference to chunks matching more query terms.
    for rank, hit in enumerate(keyword_hits, start=1):
        hit["keyword_score"] = hit["matched_terms"] / max(len(query_terms), 1)

    # 4. Combine semantic and keyword rankings
    combined = {}

    for rank, hit in enumerate(semantic_hits, start=1):
        combined[hit["id"]] = {
            **hit,
            "hybrid_score": 1 / (60 + rank)
        }

    for rank, hit in enumerate(keyword_hits, start=1):
        if hit["id"] not in combined:
            combined[hit["id"]] = {
                **hit,
                "hybrid_score": 0
            }

        combined[hit["id"]]["hybrid_score"] += 1 / (60 + rank)

    # Combine semantic and keyword scores.
    keyword_scores = {
        hit["id"]: hit["keyword_score"]
        for hit in keyword_hits
    }

    for hit in combined.values():
        hit["hybrid_score"] += (
            0.5 * keyword_scores.get(hit["id"], 0)
        )

    # Prefer the MUDRA document for MUDRA-related questions.
    if "mudra" in query_terms or "pmmy" in query_terms:
        for hit in combined.values():
            if hit["source"] == "pmmy_faq.pdf":
                hit["hybrid_score"] += 0.02

    # 5. Return the highest-ranked chunks
    ranked_hits = sorted(
        combined.values(),
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    results = []

    for hit in ranked_hits[:n_results]:
        hit.pop("hybrid_score", None)
        hit.pop("matched_terms", None)
        results.append(hit)

    return results




