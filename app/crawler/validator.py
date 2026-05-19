import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

from app.crawler.exceptions import DNSResolutionError, URLValidationError

SUPPORTED_SCHEMES = {"http", "https"}


def _is_safe_ip(address: str) -> bool:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    return parsed.is_global


def _validate_url_shape(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme.lower() not in SUPPORTED_SCHEMES:
        raise URLValidationError("Only http and https URLs are supported.")
    if not parsed.hostname:
        raise URLValidationError("URL must include a hostname.")
    if parsed.username or parsed.password:
        raise URLValidationError("URLs with embedded credentials are not supported.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".localhost"):
        raise URLValidationError("Localhost targets are not allowed.")
    return hostname


async def resolve_public_addresses(hostname: str) -> list[str]:
    try:
        addrinfo = await asyncio.to_thread(
            socket.getaddrinfo,
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise DNSResolutionError(f"Unable to resolve hostname: {hostname}") from exc

    addresses = sorted({item[4][0] for item in addrinfo})
    if not addresses:
        raise DNSResolutionError(f"Hostname resolved no addresses: {hostname}")
    unsafe = [address for address in addresses if not _is_safe_ip(address)]
    if unsafe:
        raise URLValidationError("URL resolves to non-public network space.")
    return addresses


async def validate_public_url(url: str) -> str:
    hostname = _validate_url_shape(url)
    await resolve_public_addresses(hostname)
    return url
