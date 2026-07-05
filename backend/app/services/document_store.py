from app.services.supabase_client import get_supabase_client


def create_document(filename: str) -> str:
    """
    Inserts a new document record and returns its generated UUID.
    """
    client = get_supabase_client()
    result = client.table("documents").insert({"filename": filename}).execute()
    return result.data[0]["id"]


def insert_chunks(document_id: str, chunks: list[str], embeddings: list[list[float]]) -> int:
    """
    Inserts chunk records linked to a document, each with its corresponding embedding.
    Returns the number of chunks inserted.
    """
    client = get_supabase_client()

    rows = [
        {
            "document_id": document_id,
            "content": chunk,
            "embedding": embedding
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    result = client.table("chunks").insert(rows).execute()
    return len(result.data)


def list_documents() -> list[dict]:
    """
    Returns all indexed documents.
    """
    client = get_supabase_client()
    result = client.table("documents").select("*").execute()
    return result.data


def delete_document(document_id: str) -> None:
    """
    Deletes a document and its chunks (cascade handled by FK constraint in schema).
    """
    client = get_supabase_client()
    client.table("documents").delete().eq("id", document_id).execute()