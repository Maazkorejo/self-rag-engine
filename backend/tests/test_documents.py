from unittest.mock import patch
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------- GET /documents success ----------

@patch("app.routes.documents.list_documents")
def test_get_documents_success(mock_list, client):
    mock_list.return_value = [
        {"id": "doc-1", "filename": "file1.txt", "created_at": "2026-01-01T00:00:00"},
        {"id": "doc-2", "filename": "file2.pdf", "created_at": "2026-01-02T00:00:00"},
    ]

    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2
    assert len(data["documents"]) == 2


# ---------- GET /documents empty ----------

@patch("app.routes.documents.list_documents")
def test_get_documents_empty(mock_list, client):
    mock_list.return_value = []

    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 0
    assert data["documents"] == []


# ---------- GET /documents internal failure ----------

@patch("app.routes.documents.list_documents")
def test_get_documents_error(mock_list, client):
    mock_list.side_effect = Exception("Database unreachable")

    response = client.get("/api/v1/documents")

    assert response.status_code == 500
    assert "Failed to list documents" in response.get_json()["error"]


# ---------- DELETE /documents/:id success ----------

@patch("app.routes.documents.delete_document")
def test_delete_document_success(mock_delete, client):
    mock_delete.return_value = None

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"]
    mock_delete.assert_called_once_with("doc-1")


# ---------- DELETE /documents/:id internal failure ----------

@patch("app.routes.documents.delete_document")
def test_delete_document_error(mock_delete, client):
    mock_delete.side_effect = Exception("Delete failed")

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 500
    assert "Failed to delete document" in response.get_json()["error"]