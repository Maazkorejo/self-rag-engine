from unittest.mock import patch, MagicMock
from app.services.auth import hash_key, verify_api_key
from app import create_app


# ---------- hash_key ----------

def test_hash_key_is_deterministic():
    key = "my-secret-key"
    assert hash_key(key) == hash_key(key)


def test_hash_key_different_inputs_differ():
    assert hash_key("key-one") != hash_key("key-two")


# ---------- verify_api_key ----------

def test_verify_api_key_empty_returns_false():
    assert verify_api_key("") is False
    assert verify_api_key(None) is False


@patch("app.services.auth.get_supabase_client")
def test_verify_api_key_valid_key(mock_get_client):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": "some-id"}]
    mock_get_client.return_value = mock_client

    assert verify_api_key("valid-key") is True


@patch("app.services.auth.get_supabase_client")
def test_verify_api_key_invalid_key(mock_get_client):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    mock_get_client.return_value = mock_client

    assert verify_api_key("invalid-key") is False


# ---------- require_api_key decorator (integration via a real protected route) ----------

@patch("app.services.auth_decorator.verify_api_key")
def test_decorator_rejects_missing_header(mock_verify):
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/v1/documents")
        assert response.status_code == 401
        assert "Missing or malformed" in response.get_json()["error"]


@patch("app.services.auth_decorator.verify_api_key")
def test_decorator_rejects_malformed_header(mock_verify):
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/v1/documents", headers={"Authorization": "NotBearer abc"})
        assert response.status_code == 401


@patch("app.routes.documents.list_documents")
@patch("app.services.auth_decorator.verify_api_key")
def test_decorator_accepts_valid_key(mock_verify, mock_list):
    mock_verify.return_value = True
    mock_list.return_value = []

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/v1/documents", headers={"Authorization": "Bearer some-key"})
        assert response.status_code == 200


@patch("app.services.auth_decorator.verify_api_key")
def test_decorator_rejects_invalid_key(mock_verify):
    mock_verify.return_value = False

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/v1/documents", headers={"Authorization": "Bearer wrong-key"})
        assert response.status_code == 401
        assert "Invalid or inactive" in response.get_json()["error"]