## 1. Project Setup

- [x] 1.1 Add Python project configuration with FastAPI, Uvicorn, Pydantic v2, httpx, BeautifulSoup4, lxml, Playwright, and test dependencies.
- [x] 1.2 Create the application package structure for API routes, schemas, crawler services, validation, extraction, and tests.
- [x] 1.3 Add a FastAPI application entrypoint that exposes generated OpenAPI documentation.

## 2. API Contract and Error Model

- [x] 2.1 Define Pydantic request and response schemas for crawl input, successful crawl data, extracted links, extracted images, metadata, and structured errors.
- [x] 2.2 Implement typed crawler exceptions for URL validation, DNS/network failures, HTTP failures, static timeout, dynamic timeout, total timeout, and rendering errors.
- [x] 2.3 Add the `POST /crawl` route and map crawler exceptions to predictable HTTP error responses.

## 3. URL Validation and Fetching

- [x] 3.1 Implement URL validation for supported schemes, hostname presence, localhost rejection, and public-address enforcement.
- [x] 3.2 Resolve hostnames and reject loopback, private, link-local, multicast, reserved, and otherwise unsafe network addresses before outbound requests.
- [x] 3.3 Implement the async static fetcher with a 20-second timeout, browser-like request headers, response metadata capture, HTML capture, and redirect safety checks.
- [x] 3.4 Add handling for DNS failures, blocked responses, network errors, and oversized or non-HTML responses.

## 4. Crawl Pipeline

- [x] 4.1 Implement render-mode detection heuristics for empty body, low visible text, and SPA mount nodes without relying on script tag signals.
- [x] 4.2 Implement the Playwright dynamic renderer with browser-like context, a 20-second timeout, and rendered HTML extraction.
- [x] 4.3 Implement the BeautifulSoup-based extractor for title, description, body text, headings, links, images, and metadata.
- [x] 4.4 Implement the crawl orchestrator that applies the 45-second total timeout, runs static-first crawling, invokes dynamic rendering when needed, and returns normalized output with `renderMode`.

## 5. Runtime and Deployment Documentation

- [x] 5.1 Document local setup, dependency installation, Playwright browser installation, and Uvicorn startup.
- [x] 5.2 Document the `POST /crawl` request and response examples, including `renderMode` and structured errors.
- [x] 5.3 Add deployment notes for running on a free-tier cloud platform with required runtime, startup command, and browser dependency considerations.