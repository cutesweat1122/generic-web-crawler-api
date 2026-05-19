# Generic Web Crawler API

FastAPI service that accepts a public URL, fetches the page, detects whether browser rendering is needed, and returns normalized structured metadata.

## Features

- `POST /crawl` endpoint for arbitrary public `http` and `https` URLs.
- SSRF-focused URL validation for unsupported schemes, localhost, private IPs, and unsafe redirects.
- Static-first crawling with `httpx`.
- Dynamic fallback rendering with Playwright for JavaScript-heavy pages.
- BeautifulSoup extraction for title, description, body text, headings, links, images, and, metadata.
- Structured error responses for validation, DNS, network, HTTP, timeout, and rendering failures.

## Local Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

Start the API:

```bash
uvicorn app.main:app --reload
```

OpenAPI documentation is available at:

- `http://127.0.0.1:8000/docs`

## API

Public API base URL:

```text
https://generic-web-crawler-api.onrender.com
```

### `POST /crawl`

Endpoint:

```text
https://generic-web-crawler-api.onrender.com/crawl
```

Request:

```json
{
  "url": "https://example.com"
}
```

Successful response:

```json
{
  "success": true,
  "data": {
    "url": "https://example.com/",
    "title": "Example Domain",
    "description": "",
    "body": "Example Domain This domain is for use in illustrative examples in documents.",
    "headings": ["Example Domain"],
    "links": [
      {
        "text": "More information...",
        "href": "https://www.iana.org/domains/example"
      }
    ],
    "images": [],
    "metadata": {},
    "renderMode": "static"
  }
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "category": "url_validation",
    "message": "Only http and https URLs are supported."
  }
}
```

Common error categories include `url_validation`, `dns_failure`, `network_error`, `http_error`, `static_timeout`, `dynamic_timeout`, `total_timeout`, and `rendering_error`.

## Deployment Notes

The app can run on free-tier platforms that support Python web services. Use:

- Runtime: Python 3.11+
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Browser setup: run `playwright install chromium` during build or release setup

Playwright needs system browser dependencies on some hosts. If the platform does not provide them automatically, use its documented Playwright build image or install command before starting the service.