import pytest

from app.crawler.exceptions import URLValidationError
from app.crawler.validator import _validate_url_shape


def test_rejects_unsupported_scheme() -> None:
    with pytest.raises(URLValidationError):
        _validate_url_shape("ftp://example.com")


def test_rejects_localhost() -> None:
    with pytest.raises(URLValidationError):
        _validate_url_shape("http://localhost:8000")


def test_accepts_public_http_shape() -> None:
    assert _validate_url_shape("https://example.com/path") == "example.com"
