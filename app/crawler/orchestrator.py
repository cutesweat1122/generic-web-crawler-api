import asyncio

from app.crawler.detector import should_render_dynamic
from app.crawler.exceptions import NetworkFetchError, StaticFetchTimeoutError, TotalCrawlTimeoutError
from app.crawler.extractor import extract_content
from app.crawler.fetcher import fetch_static_html
from app.crawler.renderer import render_dynamic_html
from app.schemas import CrawlData

TOTAL_CRAWL_TIMEOUT_SECONDS = 45.0


class CrawlerOrchestrator:
    async def crawl(self, url: str) -> CrawlData:
        try:
            return await asyncio.wait_for(
                self._crawl(url),
                timeout=TOTAL_CRAWL_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            raise TotalCrawlTimeoutError("Total crawl timeout exceeded.") from exc

    async def _crawl(self, url: str) -> CrawlData:
        try:
            # try to fetch the static HTML first
            static_result = await fetch_static_html(url)
        except (NetworkFetchError, StaticFetchTimeoutError):
            # if static fetch fails due to network or timeout, render the page dynamically
            rendered_html = await render_dynamic_html(url)
            return extract_content(rendered_html, url, "dynamic")

        # if the page is dynamic, render it dynamically
        if should_render_dynamic(static_result.html):
            rendered_html = await render_dynamic_html(static_result.url)
            return extract_content(rendered_html, static_result.url, "dynamic")
        return extract_content(static_result.html, static_result.url, "static")
