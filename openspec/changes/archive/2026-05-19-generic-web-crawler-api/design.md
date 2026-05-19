## Context

The repository currently contains the requirement brief and OpenSpec scaffolding for a new FastAPI-based crawler service. The service must accept arbitrary public URLs, reject unsafe network targets, extract structured page metadata, and automatically choose between lightweight static fetching and browser-based rendering when a page appears to depend on client-side JavaScript.

The implementation is expected to run on Python 3.11+ and remain deployable on free-tier cloud platforms, so the design should minimize always-on browser cost while still supporting dynamic sites.

## Goals / Non-Goals

**Goals:**

- Provide a public REST API with `POST /crawl`.
- Use asynchronous FastAPI request handling and an async crawling pipeline.
- Validate target URLs before any outbound request to reduce SSRF risk.
- Fetch static HTML with `httpx` first and use Playwright only when dynamic rendering is needed.
- Extract and normalize title, description, body content, headings, links, images, and metadata.
- Apply stage-level timeouts for static fetch, dynamic render, and total request duration.
- Keep crawler responsibilities modular so validation, fetching, rendering, detection, extraction, and API schemas can evolve independently.

**Non-Goals:**

- Crawling multiple pages, following links recursively, or maintaining crawl jobs.
- Persisting crawl results or providing a database-backed history.
- Authenticating callers, rate limiting, or billing API usage.
- Bypassing robots, paywalls, CAPTCHAs, bot detection, or authenticated pages.
- Guaranteeing perfect extraction for every malformed or heavily protected website.

## Decisions

1. Build a FastAPI application with a small service layer.
   - Rationale: FastAPI matches the required stack, provides Pydantic validation and OpenAPI documentation, and supports async I/O for concurrent fetches.
   - Alternative considered: Flask or Django REST Framework. They add less value for this async crawler and do not align with the stated stack.

2. Make the crawler orchestrator the boundary between API and crawl internals.
   - Rationale: The API route should validate request shape and translate exceptions, while the orchestrator owns stage ordering, timeout budget, render-mode detection, and normalized output assembly.
   - Alternative considered: Implement all crawl logic in the route handler. That would make testing and future extraction extensions harder.

3. Use static-first crawling with browser fallback.
   - Rationale: Most crawl targets can be handled by `httpx` and BeautifulSoup at lower latency and memory cost. Static requests and browser rendering should use a shared browser-like request profile so ordinary sites that reject obvious bot clients are less likely to fail. Playwright should be reserved for pages whose initial HTML indicates missing or app-mounted content, or when the static client times out or hits a read failure after URL validation.
   - Alternative considered: Always use Playwright. This is simpler but significantly more expensive and less suitable for free-tier deployment.

4. Detect dynamic rendering needs with conservative HTML and DOM-content heuristics.
   - Rationale: Signals such as very low visible text, empty body, and common SPA mount nodes with little visible content are practical indicators that a rendered DOM may be needed. The detector should not classify a page as dynamic solely because it has many scripts, module scripts, or JavaScript bundle filenames.
   - Alternative considered: Require clients to specify render mode. That would push implementation knowledge onto callers and violates the autonomous detection requirement.

5. Normalize extraction from parsed HTML regardless of source.
   - Rationale: Static and dynamic flows can both produce final HTML, letting one extractor handle titles, metadata, headings, links, images, and body text consistently.
   - Alternative considered: Maintain separate extractors for static and dynamic content. This would duplicate behavior and create inconsistent responses.

6. Represent errors as typed crawler exceptions mapped to HTTP responses.
   - Rationale: DNS failures, unsupported URLs, private-network targets, HTTP failures, and timeouts need predictable API behavior and focused tests.
   - Alternative considered: Return `success: false` with HTTP 200 for every failure. That makes integration errors harder for API clients to handle.

## Risks / Trade-offs

- Dynamic rendering can exceed free-tier CPU or memory limits -> Use static-first crawling, strict timeouts, and lazy Playwright usage.
- SSR/CSR heuristics can misclassify some sites -> Include `renderMode` in responses and keep detection logic isolated for future tuning.
- URL validation can miss DNS rebinding or redirect-to-private cases -> Resolve and validate host targets before fetches and validate redirect destinations where the HTTP client exposes them.
- Some websites block obvious automated clients, time out, or return 403 -> Use a browser-like request profile for both static and dynamic requests, fall back to browser rendering for static read failures/timeouts, then surface a clear crawl error if rendering also fails.
- Large pages can produce oversized body output -> Normalize body text and apply reasonable internal truncation if shows response size risk.
- Playwright installation complicates deployment -> Document browser installation.

## Migration Plan

1. Add project packaging, dependency configuration, and application entrypoint.
2. Implement schemas, URL validation, crawler exceptions, and API route.
3. Implement static fetch, render-mode detection, dynamic renderer, extractor, and orchestrator.
4. Add deployment/runtime documentation for local execution and Playwright browser installation.

Rollback is straightforward before deployment: remove the new service files and dependencies. After deployment, roll back by redeploying the previous artifact because this change introduces a new service rather than modifying existing production behavior.

## Open Questions

- Which public cloud target will be used first for deployment packaging?
- Should response body text be capped at a fixed character limit in the initial implementation?
- Should failed upstream HTTP statuses be returned as crawler errors for all 4xx/5xx responses or only when no useful HTML can be extracted?
