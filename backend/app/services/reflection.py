from app.services.groq_client import call_groq


def should_retrieve(query: str) -> bool:
    """
    [Retrieve] — Step 1: Decide whether external knowledge is needed to answer the query.
    """
    prompt = f"""You are deciding whether external document retrieval is necessary to answer a user's query accurately.

Query: "{query}"

If answering this query requires specific facts, current information, or domain knowledge that would likely be found in a document store, respond with exactly: YES
If this query can be answered directly from general knowledge or is conversational, respond with exactly: NO

Respond with only YES or NO, nothing else."""

    result = call_groq(prompt, temperature=0.1, max_tokens=5)
    return result.strip().upper().startswith("YES")


def is_relevant(query: str, passage: str) -> bool:
    """
    [IsRel] — Step 2: Classify a retrieved passage as RELEVANT or IRRELEVANT to the query.
    """
    prompt = f"""Determine if the following passage is relevant to answering the query.

Query: "{query}"

Passage: "{passage}"

Respond with exactly RELEVANT if the passage contains information that helps answer the query.
Respond with exactly IRRELEVANT if it does not.

Respond with only one word: RELEVANT or IRRELEVANT."""

    result = call_groq(prompt, temperature=0.1, max_tokens=5)
    return result.strip().upper().startswith("RELEVANT")


def is_supported(answer: str, passages: list[str]) -> str:
    """
    [IsSup] — Step 3: Verify the generated answer is grounded in the provided passages.
    Returns one of: FULLY_SUPPORTED, PARTIALLY_SUPPORTED, NOT_SUPPORTED
    """
    context = "\n\n".join(f"Passage {i+1}: {p}" for i, p in enumerate(passages))

    prompt = f"""You are verifying whether a generated answer is factually grounded in the given passages.

Passages:
{context}

Generated Answer: "{answer}"

Classify the answer as exactly one of:
FULLY_SUPPORTED - every claim in the answer is backed by the passages
PARTIALLY_SUPPORTED - some claims are backed, others are not
NOT_SUPPORTED - the answer is not backed by the passages at all

Respond with only one of those three labels, nothing else."""

    result = call_groq(prompt, temperature=0.1, max_tokens=10).strip().upper()

    if "FULLY_SUPPORTED" in result:
        return "FULLY_SUPPORTED"
    elif "PARTIALLY_SUPPORTED" in result:
        return "PARTIALLY_SUPPORTED"
    else:
        return "NOT_SUPPORTED"


def is_useful(query: str, answer: str) -> int:
    """
    [IsUse] — Step 4: Score the final answer's utility to the user on a 1-5 scale.
    """
    prompt = f"""Rate how useful the following answer is in addressing the user's query, on a scale of 1 to 5.
1 = not useful at all, 5 = extremely useful and complete.

Query: "{query}"
Answer: "{answer}"

Respond with only a single digit from 1 to 5, nothing else."""

    result = call_groq(prompt, temperature=0.1, max_tokens=3)

    for char in result:
        if char.isdigit() and 1 <= int(char) <= 5:
            return int(char)

    return 3  # fallback default if parsing fails