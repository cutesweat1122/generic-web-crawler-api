class CrawlerError(Exception):
    category = "crawler_error"
    status_code = 502

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class URLValidationError(CrawlerError):
    category = "url_validation"
    status_code = 400


class DNSResolutionError(CrawlerError):
    category = "dns_failure"
    status_code = 400


class NetworkFetchError(CrawlerError):
    category = "network_error"
    status_code = 502


class HTTPFetchError(CrawlerError):
    category = "http_error"
    status_code = 502


class StaticFetchTimeoutError(CrawlerError):
    category = "static_timeout"
    status_code = 504


class DynamicRenderTimeoutError(CrawlerError):
    category = "dynamic_timeout"
    status_code = 504


class TotalCrawlTimeoutError(CrawlerError):
    category = "total_timeout"
    status_code = 504


class RenderingError(CrawlerError):
    category = "rendering_error"
    status_code = 502
