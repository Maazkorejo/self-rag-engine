from app.services.groq_client import call_groq


def generate_answer(query: str, passages: list[str]) -> str:
    """
    Generates a grounded answer to the query using the provided passages as context.
    If no passages are provided, generates directly from the model's own knowledge
    (used when [Retrieve] decides retrieval isn't needed).
    """
    if passages:
        context = "\n\n".join(f"Passage {i+1}: {p}" for i, p in enumerate(passages))
        prompt = f"""Answer the query using ONLY the information in the passages below. Be concise and accurate. If the passages don't fully answer the query, say what you can based on them.

Passages:
{context}

Query: "{query}"

Answer:"""
    else:
        prompt = f"""Answer the following query directly and concisely using your own knowledge.

Query: "{query}"

Answer:"""

    return call_groq(prompt, temperature=0.3, max_tokens=400)