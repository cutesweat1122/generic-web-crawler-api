from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.schemas import CrawlData, ExtractedImage, ExtractedLink, RenderMode

MAX_BODY_CHARS = 100_000


def _clean_text(value: str | None) -> str:
    # normalize whitespace
    return " ".join((value or "").split())


def _extract_description(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"name": "description"})
    if tag is None:
        tag = soup.find("meta", attrs={"property": "og:description"})
    return _clean_text(tag.get("content") if tag else "")


def _extract_metadata(soup: BeautifulSoup) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for tag in soup.find_all("meta"):
        key = tag.get("name") or tag.get("property") or tag.get("itemprop")
        content = tag.get("content")
        if key and content:
            metadata[str(key)] = _clean_text(str(content))
    return metadata


def _extract_body(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()
    return _clean_text(soup.get_text(" ", strip=True))[:MAX_BODY_CHARS]


def extract_content(html: str, url: str, render_mode: RenderMode) -> CrawlData:
    soup = BeautifulSoup(html, "lxml")
    title = _clean_text(soup.title.string if soup.title else "")

    # extract headings
    headings = [
        _clean_text(heading.get_text(" ", strip=True))
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    ]
    headings = [heading for heading in headings if heading]

    # extract links
    links: list[ExtractedLink] = []
    for anchor in soup.find_all("a", href=True):
        href = _clean_text(anchor.get("href"))
        if href:
            links.append(
                ExtractedLink(
                    text=_clean_text(anchor.get_text(" ", strip=True)),
                    href=urljoin(url, href), # builds an absolute URL from a base URL and another path
                )
            )

    # extract images
    images: list[ExtractedImage] = []
    for image in soup.find_all("img", src=True):
        src = _clean_text(image.get("src"))
        if src:
            images.append(
                ExtractedImage(
                    src=urljoin(url, src),
                    alt=_clean_text(image.get("alt")),
                )
            )

    return CrawlData(
        url=url,
        title=title,
        description=_extract_description(soup),
        body=_extract_body(soup),
        headings=headings,
        links=links,
        images=images,
        metadata=_extract_metadata(soup),
        renderMode=render_mode,
    )
