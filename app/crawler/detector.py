
from bs4 import BeautifulSoup

MIN_VISIBLE_TEXT_CHARS = 120
SPA_MOUNT_IDS = {"app", "root", "__next", "nuxt", "svelte"}


def _visible_text_length(soup: BeautifulSoup) -> int:
    # remove tags that do not represent useful visible page text
    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()
    # return remaining text length
    return len(" ".join(soup.get_text(" ", strip=True).split()))


def should_render_dynamic(html: str) -> bool:
    # HTML is empty
    if not html or not html.strip():
        return True

    soup = BeautifulSoup(html, "lxml")
    body = soup.body
    # no body or body has no text
    if body is None or not body.get_text(strip=True):
        return True

    # visible text length is less than the minimum threshold
    visible_text_length = _visible_text_length(BeautifulSoup(html, "lxml"))
    if visible_text_length < MIN_VISIBLE_TEXT_CHARS:
        return True

    # SPA mount element exists and it contains less than the minimum threshold of visible text
    for mount_id in SPA_MOUNT_IDS:
        mount = soup.find(id=mount_id)
        mount_text_length = len(mount.get_text(" ", strip=True)) if mount is not None else 0
        if mount is not None and mount_text_length < MIN_VISIBLE_TEXT_CHARS:
            return True

    return False
