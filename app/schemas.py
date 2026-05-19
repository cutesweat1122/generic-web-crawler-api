from typing import Any, Literal

from pydantic import AnyHttpUrl, BaseModel, Field


RenderMode = Literal["static", "dynamic"]


class CrawlRequest(BaseModel):
    url: AnyHttpUrl


class ExtractedLink(BaseModel):
    text: str = ""
    href: str


class ExtractedImage(BaseModel):
    src: str
    alt: str = ""


class CrawlData(BaseModel):
    url: str
    title: str = ""
    description: str = ""
    body: str = ""
    headings: list[str] = Field(default_factory=list)
    links: list[ExtractedLink] = Field(default_factory=list)
    images: list[ExtractedImage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    renderMode: RenderMode


class CrawlResponse(BaseModel):
    success: Literal[True] = True
    data: CrawlData


class ErrorDetail(BaseModel):
    category: str
    message: str


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorDetail
