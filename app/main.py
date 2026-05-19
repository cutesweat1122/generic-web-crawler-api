from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Generic Web Crawler API",
        description="Extract structured metadata from static and dynamic webpages.",
        version="0.1.0",
    )
    app.include_router(router)
    return app


app = create_app()
