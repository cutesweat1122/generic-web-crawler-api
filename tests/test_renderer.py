from app.crawler.renderer import _format_render_error, _has_usable_html, _is_http2_protocol_error


def test_detects_http2_protocol_error() -> None:
    error = Exception("Page.goto: net::ERR_HTTP2_PROTOCOL_ERROR at https://example.com")

    assert _is_http2_protocol_error(error) is True


def test_formats_missing_browser_error() -> None:
    error = Exception("Executable doesn't exist. Please run: playwright install")

    assert _format_render_error(error) == (
        "Playwright browser executable is missing. Run `playwright install chromium`."
    )


def test_detects_usable_partial_html() -> None:
    html = f"<html><body>{'article content ' * 50}</body></html>"

    assert _has_usable_html(html) is True
