from app.services.supabase_client import get_supabase_client


def log_query(query_text: str, reflection_log: list, utility_score: int) -> str:
    """
    Persists a query and its reflection trace to the query_logs table.
    Returns the generated query_id.
    """
    client = get_supabase_client()
    result = client.table("query_logs").insert({
        "query_text": query_text,
        "reflection_log": reflection_log,
        "utility_score": utility_score
    }).execute()
    return result.data[0]["id"]


def get_query_log(query_id: str) -> dict:
    """
    Retrieves a single query log by id.
    """
    client = get_supabase_client()
    result = client.table("query_logs").select("*").eq("id", query_id).execute()
    return result.data[0] if result.data else None