from app.crawler.browser_profile import BROWSER_HEADERS, CHROME_USER_AGENT
from app.crawler.exceptions import DynamicRenderTimeoutError, RenderingError

DYNAMIC_RENDER_TIMEOUT_SECONDS = 20.0
POST_COMMIT_SETTLE_MILLISECONDS = 1_500
DOMCONTENT_LOADED_TIMEOUT_MILLISECONDS = 5_000
BASE_CHROMIUM_ARGS = ["--no-sandbox", "--disable-dev-shm-usage"]


def _format_render_error(exc: Exception) -> str:
    message = str(exc).strip()
    if "Executable doesn't exist" in message or "playwright install" in message:
        return "Playwright browser executable is missing. Run `playwright install chromium`."
    if message:
        first_line = message.splitlines()[0]
        return f"Dynamic render failed: {exc.__class__.__name__}: {first_line}"
    return f"Dynamic render failed: {exc.__class__.__name__}"


def _is_http2_protocol_error(exc: Exception) -> bool:
    return "ERR_HTTP2_PROTOCOL_ERROR" in str(exc)


def _has_usable_html(html: str) -> bool:
    normalized = html.strip().lower()
    return "<body" in normalized and len(normalized) > 500


async def render_dynamic_html(url: str) -> str:
    try:
        from playwright.async_api import BrowserType
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RenderingError("Playwright is not installed.") from exc

    async def render_with_args(chromium: BrowserType, args: list[str]) -> str:
        browser = await chromium.launch(headless=True, args=args)
        try:
            context = await browser.new_context(
                user_agent=CHROME_USER_AGENT,
                extra_http_headers={
                    key: value
                    for key, value in BROWSER_HEADERS.items()
                    if key.lower() not in {"user-agent", "accept-encoding"}
                },
                locale="en-US",
                timezone_id="America/Los_Angeles",
                viewport={"width": 1366, "height": 768},
            )
            page = await context.new_page()

            async def block_heavy_assets(route):
                if route.request.resource_type in {"image", "media", "font"}:
                    await route.abort()
                    return
                await route.continue_()

            await page.route("**/*", block_heavy_assets)
            try:
                await page.goto(
                    url,
                    wait_until="commit",
                    timeout=int(DYNAMIC_RENDER_TIMEOUT_SECONDS * 1000),
                )
                try:
                    await page.wait_for_load_state(
                        "domcontentloaded",
                        timeout=DOMCONTENT_LOADED_TIMEOUT_MILLISECONDS,
                    )
                except PlaywrightTimeoutError:
                    pass
                await page.wait_for_timeout(POST_COMMIT_SETTLE_MILLISECONDS)
                return await page.content()
            except PlaywrightTimeoutError:
                html = await page.content()
                if _has_usable_html(html):
                    return html
                raise
        finally:
            await browser.close()

    try:
        async with async_playwright() as playwright:
            try:
                return await render_with_args(playwright.chromium, BASE_CHROMIUM_ARGS)
            except Exception as exc:
                if not _is_http2_protocol_error(exc):
                    raise
                return await render_with_args(
                    playwright.chromium,
                    [*BASE_CHROMIUM_ARGS, "--disable-http2"],
                )
    except PlaywrightTimeoutError as exc:
        raise DynamicRenderTimeoutError("Dynamic render timed out.") from exc
    except DynamicRenderTimeoutError:
        raise
    except Exception as exc:
        raise RenderingError(_format_render_error(exc)) from exc
