# Project Name

Generic Web Crawler API

---

# Project Overview

The objective is to build a generic web crawling service capable of extracting structured metadata from any arbitrary URL. The system must autonomously differentiate between static (Server-Side Rendered) and dynamic (Client-Side Rendered) websites. It will be exposed as a public-facing REST API.
Build a generic web crawler service that accepts any arbitrary public URL and extracts structured HTML data such as:

- Title
- Meta description
- Body content
- Headings
- Links
- Images
- Metadata

The crawler must autonomously determine whether a website is:

- Static / Server-Side Rendered (SSR)
- Dynamic / Client-Side Rendered (CSR)
and use the appropriate crawling strategy automatically.

The service should be deployable to a free-tier public cloud platform such as:

- AWS
- GCP
- Azure
- Render
- Railway
- Oracle Cloud

---

# Requirements

## Functional Requirements

- Accept any URL as input
- Fetch webpage content
- Extract meaningful structured content
- Detect SSR vs CSR automatically
- Use browser rendering for dynamic websites
- Return normalized JSON output

## Non-Functional Requirements

- Modular architecture
- Extensible extraction pipeline
- Fault tolerant

---

# Tech Stack

## Backend Framework

- Python 3.11+
- FastAPI

### Why FastAPI

- High performance async support
- Modern Python typing
- Easy API development
- Built-in OpenAPI support

## Libraries


| Component                   | Tool                       | Why It's Chosen                                                                                                                                                                                                                   |
| --------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **API Framework**           | `FastAPI` + `Uvicorn`      | Built natively on ASGI for high-performance asynchronous I/O. It handles concurrent requests without blocking, uses Pydantic for instant data validation, and automatically generates interactive Swagger API documentation.      |
| **Static Fetching (SSR)**   | `httpx`                    | A modern, fully asynchronous HTTP client that acts as a lightweight replacement for `requests`. It allows the crawler to swiftly fetch raw HTML in milliseconds with near-zero memory consumption.                                |
| **Dynamic Rendering (CSR)** | `Playwright` (Python)      | Far faster, more reliable, and less resource-heavy than Selenium. It supports native async execution, handles Single-Page Applications (React, Vue, Angular) beautifully, and handles dynamic waiting for elements automatically. |
| **HTML Parsing Engine**     | `BeautifulSoup4` (`lxml`)` | The industry standard for navigating and extracting data from DOM trees. Using the `lxml` backend ensures C-speed processing, allowing it to easily parse large or poorly structured HTML bodies.                                 |
| **Data Normalization**      | `Pydantic` (v2)            | Enforces strict type-safe schemas. It guarantees that regardless of how messy or chaotic the target website's code is, the API always returns a perfectly structured, uniform JSON output.                                        |


---

# High-Level Architecture

```text
                ┌─────────────────────┐
                │      Client         │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │     FastAPI API     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Crawl Orchestrator  │
                └──────────┬──────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌───────────────────┐             ┌────────────────────┐
│ Static Fetcher    │             │ Dynamic Renderer   │
│ httpx + BS4       │             │ Playwright         │
└─────────┬─────────┘             └─────────┬──────────┘
          │                                 │
          └──────────────┬──────────────────┘
                         ▼
               ┌──────────────────┐
               │ Content Extractor│
               └─────────┬────────┘
                         ▼
               ┌──────────────────┐
               │ Data Normalizer  │
               └─────────┬────────┘
                         ▼
               ┌──────────────────┐
               │ JSON Response    │
               └──────────────────┘
```

---

# Crawling Workflow

## Step 1 — Receive URL

Example Request:

```json
{
  "url": "https://example.com"
}
```

## Step 2 — URL Validation

Validate:

- valid protocol (`http`, `https`)
- valid hostname
- public IP only

Reject:

- localhost
- internal/private IPs
- unsupported protocols

## Step 3 — Initial Static Fetch

Perform lightweight HTTP request using `httpx`.

Collect:

- status code
- headers
- HTML content
- response size

## Step 4 — SSR vs CSR Detection

Automatically determine whether browser rendering is required.

### SSR Detection Heuristics


| Signal                   | Meaning    |
| ------------------------ | ---------- |
| Empty body               | likely CSR |
| Minimal visible text     | likely CSR |
| `id="root"`              | React SPA  |
| `id="app"`               | Vue SPA    |
| Large JS bundles         | likely CSR |
| `<script type="module">` | modern SPA |


## SSR Flow

```text
Launch Browser
      ↓
Open Page
      ↓
Wait for network idle
      ↓
Extract rendered HTML
      ↓
Parse content
```

### CSR Flow

```text
HTTP GET
   ↓
BeautifulSoup Parse
   ↓
Extract Metadata
   ↓
Return JSON
```

---

# Content Extraction

## Extracted Fields

```json
{
  "url": "",
  "title": "",
  "description": "",
  "body": "",
  "headings": [],
  "links": [],
  "images": [],
  "metadata": {}
}
```

---

# API Design

## POST `/crawl`

## Request

```json
{
  "url": "https://example.com"
}
```

## Response

```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Site",
    "description": "Example description",
    "body": "Main page content...",
    "headings": [],
    "links": [],
    "images": [],
    "renderMode": "dynamic"
  }
}
```

---

# Error Handling

throw errors if timeout, DNS failure, 403 response, etc

## Timeout Strategy


| Stage          | Timeout |
| -------------- | ------- |
| Static fetch   | 3s      |
| Dynamic render | 20s     |
| Total request  | 25s     |


