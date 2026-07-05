from unittest.mock import patch
from app.services.reflection import should_retrieve, is_relevant, is_supported, is_useful


# ---------- should_retrieve ----------

@patch("app.services.reflection.call_groq")
def test_should_retrieve_yes(mock_call):
    mock_call.return_value = "YES"
    assert should_retrieve("What were Q3 2025 revenue figures?") is True


@patch("app.services.reflection.call_groq")
def test_should_retrieve_no(mock_call):
    mock_call.return_value = "NO"
    assert should_retrieve("What is 2+2?") is False


@patch("app.services.reflection.call_groq")
def test_should_retrieve_handles_lowercase(mock_call):
    mock_call.return_value = "yes"
    assert should_retrieve("Some query") is True


# ---------- is_relevant ----------

@patch("app.services.reflection.call_groq")
def test_is_relevant_true(mock_call):
    mock_call.return_value = "RELEVANT"
    assert is_relevant("query", "passage") is True


@patch("app.services.reflection.call_groq")
def test_is_relevant_false(mock_call):
    mock_call.return_value = "IRRELEVANT"
    assert is_relevant("query", "passage") is False


# ---------- is_supported ----------

@patch("app.services.reflection.call_groq")
def test_is_supported_fully(mock_call):
    mock_call.return_value = "FULLY_SUPPORTED"
    assert is_supported("answer", ["passage"]) == "FULLY_SUPPORTED"


@patch("app.services.reflection.call_groq")
def test_is_supported_partially(mock_call):
    mock_call.return_value = "PARTIALLY_SUPPORTED"
    assert is_supported("answer", ["passage"]) == "PARTIALLY_SUPPORTED"


@patch("app.services.reflection.call_groq")
def test_is_supported_not_supported(mock_call):
    mock_call.return_value = "NOT_SUPPORTED"
    assert is_supported("answer", ["passage"]) == "NOT_SUPPORTED"


@patch("app.services.reflection.call_groq")
def test_is_supported_fallback_on_garbage(mock_call):
    mock_call.return_value = "unexpected gibberish"
    assert is_supported("answer", ["passage"]) == "NOT_SUPPORTED"


# ---------- is_useful ----------

@patch("app.services.reflection.call_groq")
def test_is_useful_valid_score(mock_call):
    mock_call.return_value = "4"
    assert is_useful("query", "answer") == 4


@patch("app.services.reflection.call_groq")
def test_is_useful_fallback_on_garbage(mock_call):
    mock_call.return_value = "not a number"
    assert is_useful("query", "answer") == 3


@patch("app.services.reflection.call_groq")
def test_is_useful_picks_first_valid_digit(mock_call):
    mock_call.return_value = "Score: 5 out of 5"
    assert is_useful("query", "answer") == 5