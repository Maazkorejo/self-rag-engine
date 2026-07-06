from app.services.reflection import should_retrieve, is_relevant, is_supported, is_useful
from app.services.retrieval import retrieve_top_k
from app.services.generation import generate_answer

MAX_RETRIES = 2


def run_self_rag_pipeline(query: str, top_k: int = 5, force_retrieve: bool = False) -> dict:
    """
    Executes the full Self-RAG reflection pipeline:
    [Retrieve] -> retrieval + [IsRel] filter -> generate -> [IsSup] verify (with retries) -> [IsUse] score

    Returns a dict matching FR-02's response spec:
    final_answer, reflection_log, utility_score, sources_used, hallucination_risk
    """
    reflection_log = []
    sources_used = []
    hallucination_risk = False

    # Step 1 — [Retrieve]
    needs_retrieval = force_retrieve or should_retrieve(query)
    reflection_log.append({"step": "Retrieve", "decision": needs_retrieval})

    relevant_passages = []

    if needs_retrieval:
        # Retrieval + Step 2 — [IsRel] filter
        retrieved_chunks = retrieve_top_k(query, top_k=top_k)

        for chunk in retrieved_chunks:
            relevant = is_relevant(query, chunk["content"])
            reflection_log.append({
                "step": "IsRel",
                "chunk_id": chunk["id"],
                "relevant": relevant
            })
            if relevant:
                relevant_passages.append(chunk["content"])
                sources_used.append(chunk["id"])

    # Step 3 — Generate + [IsSup] verify, with retry loop
    answer = generate_answer(query, relevant_passages)
    support_status = is_supported(answer, relevant_passages) if relevant_passages else "FULLY_SUPPORTED"
    reflection_log.append({"step": "IsSup", "attempt": 1, "status": support_status})

    attempt = 1
    while support_status == "NOT_SUPPORTED" and attempt <= MAX_RETRIES and relevant_passages:
        attempt += 1
        answer = generate_answer(query, relevant_passages)
        support_status = is_supported(answer, relevant_passages)
        reflection_log.append({"step": "IsSup", "attempt": attempt, "status": support_status})

    if support_status == "NOT_SUPPORTED":
        hallucination_risk = True

    # Step 4 — [IsUse]
    utility_score = is_useful(query, answer)
    reflection_log.append({"step": "IsUse", "score": utility_score})

    return {
        "final_answer": answer,
        "reflection_log": reflection_log,
        "utility_score": utility_score,
        "sources_used": sources_used,
        "hallucination_risk": hallucination_risk
    }