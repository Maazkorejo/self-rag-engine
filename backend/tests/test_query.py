from unittest.mock import patch
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


FAKE_PIPELINE_RESULT = {
    "final_answer": "Paris is the capital of France.",
    "reflection_log": [{"step": "Retrieve", "decision": False}],
    "utility_score": 5,
    "sources_used": [],
    "hallucination_risk": False
}


# ---------- POST /query success ----------

@patch("app.routes.query.log_query")
@patch("app.routes.query.run_self_rag_pipeline")
def test_query_success(mock_pipeline, mock_log, client):
    mock_pipeline.return_value = FAKE_PIPELINE_RESULT
    mock_log.return_value = "fake-query-id"

    response = client.post("/api/v1/query", json={"query": "What is the capital of France?"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["query_id"] == "fake-query-id"
    assert data["final_answer"] == "Paris is the capital of France."
    assert data["utility_score"] == 5
    assert data["hallucination_risk"] is False


# ---------- POST /query missing body ----------

def test_query_no_body(client):
    response = client.post("/api/v1/query")
    assert response.status_code == 400
    assert "error" in response.get_json()


# ---------- POST /query empty query string ----------

def test_query_empty_string(client):
    response = client.post("/api/v1/query", json={"query": "   "})
    assert response.status_code == 400
    assert "error" in response.get_json()


# ---------- POST /query missing 'query' key ----------

def test_query_missing_key(client):
    response = client.post("/api/v1/query", json={"top_k": 5})
    assert response.status_code == 400
    assert "error" in response.get_json()


# ---------- POST /query passes optional params through ----------

@patch("app.routes.query.log_query")
@patch("app.routes.query.run_self_rag_pipeline")
def test_query_passes_top_k_and_force_retrieve(mock_pipeline, mock_log, client):
    mock_pipeline.return_value = FAKE_PIPELINE_RESULT
    mock_log.return_value = "fake-query-id"

    client.post("/api/v1/query", json={"query": "test", "top_k": 3, "force_retrieve": True})

    mock_pipeline.assert_called_once_with("test", top_k=3, force_retrieve=True)


# ---------- POST /query internal failure ----------

@patch("app.routes.query.run_self_rag_pipeline")
def test_query_internal_error(mock_pipeline, client):
    mock_pipeline.side_effect = Exception("Pipeline exploded")

    response = client.post("/api/v1/query", json={"query": "test"})

    assert response.status_code == 500
    assert "Query failed" in response.get_json()["error"]


# ---------- GET /reflection/:id found ----------

@patch("app.routes.query.get_query_log")
def test_get_reflection_found(mock_get_log, client):
    mock_get_log.return_value = {
        "id": "fake-id",
        "query_text": "test query",
        "reflection_log": [],
        "utility_score": 4
    }

    response = client.get("/api/v1/reflection/fake-id")

    assert response.status_code == 200
    assert response.get_json()["id"] == "fake-id"


# ---------- GET /reflection/:id not found ----------

@patch("app.routes.query.get_query_log")
def test_get_reflection_not_found(mock_get_log, client):
    mock_get_log.return_value = None

    response = client.get("/api/v1/reflection/nonexistent-id")

    assert response.status_code == 404
    assert "error" in response.get_json()