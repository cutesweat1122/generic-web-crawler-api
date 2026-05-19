from app.crawler.extractor import extract_content


def test_extracts_structured_content() -> None:
    html = """
    <html>
      <head>
        <title>Example Site</title>
        <meta name="description" content="Example description">
        <meta property="og:type" content="website">
      </head>
      <body>
        <h1>Main Heading</h1>
        <a href="/about">About us</a>
        <img src="/logo.png" alt="Logo">
        <p>Main page content.</p>
      </body>
    </html>
    """

    data = extract_content(html, "https://example.com", "static")

    assert data.title == "Example Site"
    assert data.description == "Example description"
    assert data.headings == ["Main Heading"]
    assert data.links[0].href == "https://example.com/about"
    assert data.images[0].src == "https://example.com/logo.png"
    assert data.metadata["og:type"] == "website"
    assert data.renderMode == "static"
