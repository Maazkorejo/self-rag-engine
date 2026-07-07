import hashlib
from app.services.supabase_client import get_supabase_client


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def verify_api_key(raw_key: str) -> bool:
    """
    Checks if the given raw API key matches an active hashed key in Supabase.
    """
    if not raw_key:
        return False

    client = get_supabase_client()
    key_hash = hash_key(raw_key)

    result = client.table("api_keys").select("id").eq("key_hash", key_hash).eq("is_active", True).execute()

    return len(result.data) > 0