import asyncio

import pytest

from app.crawler.exceptions import NetworkFetchError, StaticFetchTimeoutError
from app.crawler.orchestrator import CrawlerOrchestrator


def test_static_timeout_falls_back_to_dynamic_render(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fail_static_fetch(url: str):
        raise StaticFetchTimeoutError("Static fetch timed out.")

    async def render_dynamic(url: str) -> str:
        return "<html><head><title>Rendered</title></head><body><h1>Rendered page</h1></body></html>"

    monkeypatch.setattr("app.crawler.orchestrator.fetch_static_html", fail_static_fetch)
    monkeypatch.setattr("app.crawler.orchestrator.render_dynamic_html", render_dynamic)

    data = asyncio.run(CrawlerOrchestrator().crawl("https://example.com"))

    assert data.renderMode == "dynamic"
    assert data.title == "Rendered"


def test_network_fetch_error_falls_back_to_dynamic_render(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_static_fetch(url: str):
        raise NetworkFetchError("Static fetch failed: ReadError")

    async def render_dynamic(url: str) -> str:
        return "<html><head><title>Recovered</title></head><body><p>Rendered body</p></body></html>"

    monkeypatch.setattr("app.crawler.orchestrator.fetch_static_html", fail_static_fetch)
    monkeypatch.setattr("app.crawler.orchestrator.render_dynamic_html", render_dynamic)

    data = asyncio.run(CrawlerOrchestrator().crawl("https://example.com"))

    assert data.renderMode == "dynamic"
    assert data.title == "Recovered"
