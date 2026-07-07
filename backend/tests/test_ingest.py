import io
from unittest.mock import patch
import pytest
from app import create_app

AUTH_HEADER = {"Authorization": "Bearer fake-test-key"}


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def make_file(filename: str, content: bytes):
    return {"file": (io.BytesIO(content), filename)}


# ---------- Success case ----------

@patch("app.services.auth_decorator.verify_api_key")
@patch("app.routes.ingest.insert_chunks")
@patch("app.routes.ingest.create_document")
@patch("app.routes.ingest.generate_embeddings_batch")
@patch("app.routes.ingest.chunk_text")
@patch("app.routes.ingest.extract_text")
def test_ingest_success(mock_extract, mock_chunk, mock_embed, mock_create_doc, mock_insert, mock_auth, client):
    mock_auth.return_value = True
    mock_extract.return_value = "Some extracted text content."
    mock_chunk.return_value = ["chunk one", "chunk two"]
    mock_embed.return_value = [[0.1] * 384, [0.2] * 384]
    mock_create_doc.return_value = "fake-document-id"
    mock_insert.return_value = 2

    response = client.post(
        "/api/v1/ingest",
        data=make_file("test.txt", b"Some raw file bytes"),
        content_type="multipart/form-data",
        headers=AUTH_HEADER
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["document_id"] == "fake-document-id"
    assert data["chunk_count"] == 2
    assert data["filename"] == "test.txt"


# ---------- Missing file ----------

@patch("app.services.auth_decorator.verify_api_key")
def test_ingest_no_file(mock_auth, client):
    mock_auth.return_value = True
    response = client.post("/api/v1/ingest", data={}, content_type="multipart/form-data", headers=AUTH_HEADER)
    assert response.status_code == 400
    assert "error" in response.get_json()


# ---------- Empty filename ----------

@patch("app.services.auth_decorator.verify_api_key")
def test_ingest_empty_filename(mock_auth, client):
    mock_auth.return_value = True
    response = client.post(
        "/api/v1/ingest",
        data=make_file("", b"content"),
        content_type="multipart/form-data",
        headers=AUTH_HEADER
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


# ---------- Unsupported file type ----------

@patch("app.services.auth_decorator.verify_api_key")
def test_ingest_unsupported_extension(mock_auth, client):
    mock_auth.return_value = True
    response = client.post(
        "/api/v1/ingest",
        data=make_file("test.exe", b"content"),
        content_type="multipart/form-data",
        headers=AUTH_HEADER
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.get_json()["error"]


# ---------- No extractable text ----------

@patch("app.services.auth_decorator.verify_api_key")
@patch("app.routes.ingest.extract_text")
def test_ingest_empty_text(mock_extract, mock_auth, client):
    mock_auth.return_value = True
    mock_extract.return_value = "   "

    response = client.post(
        "/api/v1/ingest",
        data=make_file("test.txt", b"content"),
        content_type="multipart/form-data",
        headers=AUTH_HEADER
    )
    assert response.status_code == 400
    assert "No extractable text" in response.get_json()["error"]


# ---------- Internal failure ----------

@patch("app.services.auth_decorator.verify_api_key")
@patch("app.routes.ingest.extract_text")
def test_ingest_internal_error(mock_extract, mock_auth, client):
    mock_auth.return_value = True
    mock_extract.side_effect = Exception("Something broke")

    response = client.post(
        "/api/v1/ingest",
        data=make_file("test.txt", b"content"),
        content_type="multipart/form-data",
        headers=AUTH_HEADER
    )
    assert response.status_code == 500
    assert "Ingestion failed" in response.get_json()["error"]