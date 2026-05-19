## ADDED Requirements

### Requirement: Crawl Endpoint
The system SHALL expose a public `POST /crawl` endpoint that accepts a JSON body containing a single target URL and returns a normalized crawl response.

#### Scenario: Valid crawl request
- **WHEN** a client submits `POST /crawl` with a valid public `http` or `https` URL
- **THEN** the system SHALL attempt to crawl the URL and return a structured response containing `success` and `data` fields

#### Scenario: Invalid request body
- **WHEN** a client submits `POST /crawl` without a URL or with a malformed URL value
- **THEN** the system SHALL reject the request with a validation error response

### Requirement: URL Safety Validation
The system MUST validate target URLs before fetching and MUST reject unsupported protocols, localhost targets, private IP targets, internal network targets, and unsafe redirects.

#### Scenario: Unsupported protocol rejected
- **WHEN** a client submits a URL using a protocol other than `http` or `https`
- **THEN** the system SHALL reject the crawl before making an outbound request

#### Scenario: Private target rejected
- **WHEN** a client submits a URL that resolves to localhost, loopback, private, link-local, multicast, or otherwise non-public network space
- **THEN** the system SHALL reject the crawl before making an outbound request

#### Scenario: Unsafe redirect rejected
- **WHEN** an allowed public URL redirects to a localhost, private, internal, or unsupported target
- **THEN** the system SHALL stop the crawl and return a crawler error

### Requirement: Static Fetching
The system SHALL perform an initial lightweight static fetch for accepted URLs using an asynchronous HTTP client and a browser-like request profile.

#### Scenario: Static fetch captures HTML
- **WHEN** a public URL returns an HTML response within the static fetch timeout
- **THEN** the system SHALL capture the final URL, status code, response headers, response size, and HTML content

#### Scenario: Browser-like static request
- **WHEN** the system performs the initial static fetch
- **THEN** the request SHALL include ordinary browser headers such as user agent, accept, language, fetch metadata, and upgrade-insecure-requests headers

#### Scenario: Static fetch timeout
- **WHEN** the static fetch does not complete within 20 seconds
- **THEN** the system SHALL attempt browser rendering before returning a timeout error for the crawl

#### Scenario: Static fetch read failure
- **WHEN** the static fetch fails because the connection cannot be read reliably
- **THEN** the system SHALL attempt browser rendering before returning a network error for the crawl

### Requirement: Render Mode Detection
The system SHALL automatically determine whether the static HTML can be extracted directly or requires browser rendering.

#### Scenario: Static page detected
- **WHEN** the initial HTML contains meaningful visible text and does not match dynamic rendering heuristics
- **THEN** the system SHALL extract content from the static HTML and set `renderMode` to `static`

#### Scenario: Dynamic page detected
- **WHEN** the initial HTML is empty, has minimal visible text, or contains common SPA mount nodes with little visible content
- **THEN** the system SHALL render the page in a browser before extracting content and set `renderMode` to `dynamic`

#### Scenario: Script-only signals ignored
- **WHEN** the initial HTML contains many scripts, module scripts, or JavaScript bundle filenames but otherwise has meaningful visible content
- **THEN** the system SHALL NOT require browser rendering based only on those script signals

### Requirement: Dynamic Rendering
The system SHALL use browser rendering for pages detected as client-side rendered or for static fetches that time out or fail with read/network errors.

#### Scenario: Rendered HTML extracted
- **WHEN** a page requires browser rendering and loads within the dynamic render timeout
- **THEN** the system SHALL wait for the rendered page to settle and extract the final rendered HTML

#### Scenario: Browser-like rendering context
- **WHEN** the system renders a page with Playwright
- **THEN** the browser context SHALL use a realistic user agent, locale, timezone, viewport, and browser request headers

#### Scenario: Dynamic render timeout
- **WHEN** browser rendering does not complete within 20 seconds
- **THEN** the system SHALL return a timeout error for the crawl

### Requirement: Structured Content Extraction
The system SHALL extract meaningful structured content from the selected HTML source.

#### Scenario: Metadata extracted
- **WHEN** the selected HTML includes a title, meta description, headings, links, images, body text, and metadata tags
- **THEN** the system SHALL return those values in normalized fields named `title`, `description`, `headings`, `links`, `images`, `body`, and `metadata`

#### Scenario: Missing optional fields
- **WHEN** the selected HTML omits optional metadata such as description, headings, links, or images
- **THEN** the system SHALL return an otherwise valid normalized response with empty strings, empty arrays, or empty objects as appropriate

### Requirement: Normalized Response Shape
The system SHALL return crawl results using a stable JSON response shape.

#### Scenario: Successful response
- **WHEN** a crawl completes successfully
- **THEN** the response data SHALL include `url`, `title`, `description`, `body`, `headings`, `links`, `images`, `metadata`, and `renderMode`

#### Scenario: Failed response
- **WHEN** a crawl fails because of validation, DNS failure, timeout, forbidden response, network error, or rendering error
- **THEN** the system SHALL return a structured error response that identifies the failure category and message

### Requirement: Request Timeout Budget
The system SHALL enforce bounded crawl execution time.

#### Scenario: Total timeout exceeded
- **WHEN** the complete crawl operation exceeds 45 seconds
- **THEN** the system SHALL stop processing and return a timeout error

### Requirement: Deployable Service
The system SHALL include the runtime configuration and documentation needed to run locally and deploy to a free-tier public cloud platform.

#### Scenario: Local service startup
- **WHEN** a developer installs the project dependencies and starts the ASGI server
- **THEN** the FastAPI application SHALL serve the crawl endpoint and generated OpenAPI documentation

#### Scenario: Deployment preparation
- **WHEN** the service is prepared for deployment
- **THEN** the repository SHALL document the required Python runtime, application startup command, and Playwright browser installation step
