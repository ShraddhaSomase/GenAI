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

