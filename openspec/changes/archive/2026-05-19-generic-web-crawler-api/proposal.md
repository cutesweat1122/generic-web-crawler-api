## Why

Users need a public API that can crawl arbitrary public webpages and return useful, normalized metadata without requiring callers to know whether the target site is server-rendered or client-rendered. Building this now establishes the service contract, architecture, and implementation plan for a fault-tolerant FastAPI crawler that can support both static HTML and JavaScript-heavy sites.

## What Changes

- Add a FastAPI service exposing `POST /crawl` for URL-based crawl requests.
- Validate submitted URLs and reject unsupported schemes, localhost, and private or internal network targets.
- Fetch pages with a lightweight static HTTP strategy first.
- Detect when the static response appears to require browser rendering for client-side content.
- Render dynamic pages with Playwright when required.
- Extract normalized fields including title, description, body content, headings, links, images, and metadata.
- Return structured success and error responses with timeout and fetch failure handling.
- Package the service so it can be deployed on a free-tier public cloud platform.

## Capabilities

### New Capabilities

- `web-crawling-api`: Covers public crawl request handling, URL validation, SSR/CSR detection, static fetching, dynamic rendering, content extraction, response normalization, and crawler error behavior.

### Modified Capabilities

- None.

## Impact

- Adds a Python 3.11+ FastAPI backend with async request handling.
- Adds crawler dependencies including `httpx`, `beautifulsoup4`, `lxml`, Pydantic v2, Uvicorn, and Playwright.
- Introduces service modules for validation, crawl orchestration, static fetching, dynamic rendering, extraction, schemas, and API routing.
- Adds API documentation through FastAPI OpenAPI generation.
