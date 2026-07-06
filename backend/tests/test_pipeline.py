from unittest.mock import patch
from app.services.pipeline import run_self_rag_pipeline


# ---------- Retrieval not needed ----------

@patch("app.services.pipeline.is_useful")
@patch("app.services.pipeline.generate_answer")
@patch("app.services.pipeline.should_retrieve")
def test_pipeline_no_retrieval_needed(mock_should_retrieve, mock_generate, mock_useful):
    mock_should_retrieve.return_value = False
    mock_generate.return_value = "Paris is the capital of France."
    mock_useful.return_value = 5

    result = run_self_rag_pipeline("What is the capital of France?")

    assert result["final_answer"] == "Paris is the capital of France."
    assert result["sources_used"] == []
    assert result["hallucination_risk"] is False
    assert result["utility_score"] == 5
    assert result["reflection_log"][0] == {"step": "Retrieve", "decision": False}


# ---------- Retrieval needed, passages filtered ----------

@patch("app.services.pipeline.is_useful")
@patch("app.services.pipeline.is_supported")
@patch("app.services.pipeline.generate_answer")
@patch("app.services.pipeline.is_relevant")
@patch("app.services.pipeline.retrieve_top_k")
@patch("app.services.pipeline.should_retrieve")
def test_pipeline_retrieval_with_relevant_passage(
    mock_should_retrieve, mock_retrieve, mock_relevant, mock_generate, mock_supported, mock_useful
):
    mock_should_retrieve.return_value = True
    mock_retrieve.return_value = [
        {"id": "chunk-1", "content": "Relevant passage content."},
        {"id": "chunk-2", "content": "Irrelevant passage content."},
    ]
    mock_relevant.side_effect = [True, False]
    mock_generate.return_value = "Grounded answer."
    mock_supported.return_value = "FULLY_SUPPORTED"
    mock_useful.return_value = 4

    result = run_self_rag_pipeline("Some query", top_k=2)

    assert result["sources_used"] == ["chunk-1"]
    assert result["final_answer"] == "Grounded answer."
    assert result["hallucination_risk"] is False
    assert result["utility_score"] == 4


# ---------- force_retrieve bypasses should_retrieve ----------

@patch("app.services.pipeline.is_useful")
@patch("app.services.pipeline.is_supported")
@patch("app.services.pipeline.generate_answer")
@patch("app.services.pipeline.is_relevant")
@patch("app.services.pipeline.retrieve_top_k")
@patch("app.services.pipeline.should_retrieve")
def test_pipeline_force_retrieve_bypasses_check(
    mock_should_retrieve, mock_retrieve, mock_relevant, mock_generate, mock_supported, mock_useful
):
    mock_should_retrieve.return_value = False
    mock_retrieve.return_value = [{"id": "chunk-1", "content": "Some content."}]
    mock_relevant.return_value = True
    mock_generate.return_value = "Answer."
    mock_supported.return_value = "FULLY_SUPPORTED"
    mock_useful.return_value = 5

    result = run_self_rag_pipeline("Query", force_retrieve=True)

    assert result["reflection_log"][0]["decision"] is True
    assert result["sources_used"] == ["chunk-1"]


# ---------- Retry loop on NOT_SUPPORTED, eventually succeeds ----------

@patch("app.services.pipeline.is_useful")
@patch("app.services.pipeline.is_supported")
@patch("app.services.pipeline.generate_answer")
@patch("app.services.pipeline.is_relevant")
@patch("app.services.pipeline.retrieve_top_k")
@patch("app.services.pipeline.should_retrieve")
def test_pipeline_retry_succeeds_on_second_attempt(
    mock_should_retrieve, mock_retrieve, mock_relevant, mock_generate, mock_supported, mock_useful
):
    mock_should_retrieve.return_value = True
    mock_retrieve.return_value = [{"id": "chunk-1", "content": "Passage."}]
    mock_relevant.return_value = True
    mock_generate.side_effect = ["Bad answer.", "Good answer."]
    mock_supported.side_effect = ["NOT_SUPPORTED", "FULLY_SUPPORTED"]
    mock_useful.return_value = 4

    result = run_self_rag_pipeline("Query")

    assert result["final_answer"] == "Good answer."
    assert result["hallucination_risk"] is False
    assert mock_generate.call_count == 2

    isup_steps = [s for s in result["reflection_log"] if s["step"] == "IsSup"]
    assert len(isup_steps) == 2
    assert isup_steps[0]["attempt"] == 1
    assert isup_steps[1]["attempt"] == 2


# ---------- Retry loop exhausted, hallucination_risk flagged ----------

@patch("app.services.pipeline.is_useful")
@patch("app.services.pipeline.is_supported")
@patch("app.services.pipeline.generate_answer")
@patch("app.services.pipeline.is_relevant")
@patch("app.services.pipeline.retrieve_top_k")
@patch("app.services.pipeline.should_retrieve")
def test_pipeline_retry_exhausted_flags_hallucination(
    mock_should_retrieve, mock_retrieve, mock_relevant, mock_generate, mock_supported, mock_useful
):
    mock_should_retrieve.return_value = True
    mock_retrieve.return_value = [{"id": "chunk-1", "content": "Passage."}]
    mock_relevant.return_value = True
    mock_generate.return_value = "Ungrounded answer."
    mock_supported.return_value = "NOT_SUPPORTED"
    mock_useful.return_value = 2

    result = run_self_rag_pipeline("Query")

    assert result["hallucination_risk"] is True
    assert mock_generate.call_count == 3  # initial attempt + 2 retries (MAX_RETRIES = 2)

    isup_steps = [s for s in result["reflection_log"] if s["step"] == "IsSup"]
    assert len(isup_steps) == 3


# ---------- No relevant passages found after filtering ----------

@patch("app.services.pipeline.is_useful")
@patch("app.services.pipeline.generate_answer")
@patch("app.services.pipeline.is_relevant")
@patch("app.services.pipeline.retrieve_top_k")
@patch("app.services.pipeline.should_retrieve")
def test_pipeline_no_relevant_passages(
    mock_should_retrieve, mock_retrieve, mock_relevant, mock_generate, mock_useful
):
    mock_should_retrieve.return_value = True
    mock_retrieve.return_value = [{"id": "chunk-1", "content": "Irrelevant."}]
    mock_relevant.return_value = False
    mock_generate.return_value = "Fallback answer."
    mock_useful.return_value = 3

    result = run_self_rag_pipeline("Query")

    assert result["sources_used"] == []
    assert result["hallucination_risk"] is False  # no passages to violate, so defaults FULLY_SUPPORTED
    assert result["final_answer"] == "Fallback answer."