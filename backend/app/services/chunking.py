def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """
    Splits text into overlapping chunks based on whitespace-separated tokens.
    Matches PRD spec: 512-token segments with 64-token overlap.
    """
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

        start = end - overlap

    return chunks