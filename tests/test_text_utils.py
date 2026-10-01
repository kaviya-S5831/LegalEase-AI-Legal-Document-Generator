from backend.services.text_utils import sanitize_text, terms_from_semicolon_text


def test_sanitize_text():
    result = sanitize_text("Hello\u2019s  world\u2014test")
    assert result == "Hello's world-test"


def test_terms_from_semicolon_text():
    assert terms_from_semicolon_text("One; Two ; ; Three") == ["One", "Two", "Three"]
