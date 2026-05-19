from app.crawler.detector import should_render_dynamic


def test_detects_static_html() -> None:
    html = """
    <html><body>
      <h1>Example</h1>
      <p>This page has enough server-rendered text to be extracted without a browser.
      It includes meaningful content, navigation, and explanatory copy for crawlers.
      The visible text is intentionally long enough to cross the static threshold.</p>
    </body></html>
    """

    assert should_render_dynamic(html) is False


def test_detects_spa_mount() -> None:
    html = """
    <html><body><div id="root"></div><script type="module" src="/assets/app.js"></script></body></html>
    """

    assert should_render_dynamic(html) is True
