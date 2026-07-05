from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model():
    """
    Lazily loads the sentence-transformers model.
    all-MiniLM-L6-v2 produces 384-dim embeddings, matching the pgvector column in schema.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> list[float]:
    """
    Generates a 384-dimensional embedding vector for the given text.
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for multiple texts in a single batched call — more efficient
    than calling generate_embedding() in a loop.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()