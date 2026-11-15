"""Generate text embeddings using Sentence Transformers."""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load the model
model = SentenceTransformer(MODEL_NAME)


def embed_texts(texts):
    """Convert a list of text strings into embedding vectors."""
    if not texts:
        return []

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
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
