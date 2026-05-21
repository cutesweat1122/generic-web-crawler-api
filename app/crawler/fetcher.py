from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from app.crawler.browser_profile import BROWSER_HEADERS
from app.crawler.exceptions import (
    HTTPFetchError,
    NetworkFetchError,
    StaticFetchTimeoutError,
    URLValidationError,
)
from app.crawler.validator import validate_public_url

STATIC_FETCH_TIMEOUT_SECONDS = 20.0
MAX_RESPONSE_BYTES = 8_000_000
MAX_REDIRECTS = 5


@dataclass(frozen=True)
class StaticFetchResult:
    url: str
    status_code: int
    headers: dict[str, str]
    html: str
    response_size: int


def _looks_like_html(content_type: str, body: str) -> bool:
    if "html" in content_type.lower():
        return True
    return body.lstrip().startswith(("<!doctype html", "<html", "<head", "<body"))


async def fetch_static_html(url: str) -> StaticFetchResult:
    await validate_public_url(url)

    current_url = url
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(STATIC_FETCH_TIMEOUT_SECONDS),
            follow_redirects=False,
            headers=BROWSER_HEADERS,
        ) as client:
            for _ in range(MAX_REDIRECTS + 1):
                response = await client.get(current_url)

                # follow redirects
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise HTTPFetchError("Redirect response did not include a location header.")
                    current_url = urljoin(str(response.url), location)
                    await validate_public_url(current_url)
                    continue

                # handle error responses
                if response.status_code >= 400:
                    raise HTTPFetchError(f"Upstream returned HTTP {response.status_code}.")

                # rejects oversized responses
                content = response.content
                if len(content) > MAX_RESPONSE_BYTES:
                    raise HTTPFetchError("Response exceeded maximum supported size.")

                # rejects non-HTML responses
                html = response.text
                content_type = response.headers.get("content-type", "")
                if content_type and not _looks_like_html(content_type, html):
                    raise HTTPFetchError("Upstream response is not HTML content.")

                return StaticFetchResult(
                    url=str(response.url),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    html=html,
                    response_size=len(content),
                )
    except httpx.TimeoutException as exc:
        raise StaticFetchTimeoutError("Static fetch timed out.") from exc
    except httpx.RequestError as exc:
        raise NetworkFetchError(f"Static fetch failed: {exc.__class__.__name__}") from exc

    raise URLValidationError("Too many redirects while validating target URL.")
