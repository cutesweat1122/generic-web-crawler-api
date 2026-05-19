from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.crawler.exceptions import CrawlerError
from app.crawler.orchestrator import CrawlerOrchestrator
from app.schemas import CrawlRequest, CrawlResponse, ErrorResponse

router = APIRouter()


@router.post(
    "/crawl",
    response_model=CrawlResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}, 504: {"model": ErrorResponse}},
)
async def crawl(request: CrawlRequest) -> CrawlResponse | JSONResponse:
    orchestrator = CrawlerOrchestrator()
    try:
        data = await orchestrator.crawl(str(request.url))
    except CrawlerError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "category": exc.category,
                    "message": exc.message,
                },
            },
        )
    return CrawlResponse(data=data)
