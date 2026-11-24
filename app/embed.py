"""Generate text embeddings using Sentence Transformers.

The model is loaded lazily on first use so the module can be imported
in CI environments where sentence-transformers is not installed,
as long as embed_texts() is never actually called (tests mock it).
"""

from __future__ import annotations

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts):
    """Convert a list of text strings into embedding vectors."""
    if not texts:
        return []

    model = _get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return embeddings.tolist()


def embed_documents(documents):
    """Generate embeddings for document chunks."""
    texts = [document["text"] for document in documents]
    return embed_texts(texts)


if __name__ == "__main__":
    from app.chunking import load_documents

    documents = load_documents()
    embeddings = embed_documents(documents)

    print("\nEmbedding completed!")
    print("Total documents:", len(documents))
    print("Total embeddings:", len(embeddings))

    if embeddings:
        print("Vector dimensions:", len(embeddings[0]))
        print("First vector sample:", embeddings[0][:5])
