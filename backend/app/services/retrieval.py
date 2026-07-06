from app.services.supabase_client import get_supabase_client
from app.services.embeddings import generate_embedding


def retrieve_top_k(query: str, top_k: int = 5) -> list[dict]:
    """
    Embeds the query and retrieves the top-k most similar chunks from Supabase
    using pgvector cosine similarity via the match_chunks RPC function.

    Returns a list of dicts: {id, document_id, content, similarity}
    """
    client = get_supabase_client()
    query_embedding = generate_embedding(query)

    result = client.rpc(
        "match_chunks",
        {"query_embedding": query_embedding, "match_count": top_k}
    ).execute()

    return result.data