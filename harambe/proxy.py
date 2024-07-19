from urllib.parse import urlparse

from playwright.async_api import ProxySettings


def proxy_from_url(url: str) -> ProxySettings:
    parsed = urlparse(url, allow_fragments=False)

    if not parsed.hostname:
        parsed = urlparse(f"http://{url}", allow_fragments=False)

    if not all(
        [
            parsed.hostname,
            parsed.username,
            parsed.password,
        ]
    ):
        raise ValueError(f"Invalid proxy URL: {url}")

    proxy: ProxySettings = {
        "server": parsed.hostname,  # type: ignore
        "username": parsed.username,
        "password": parsed.password,
    }

    if parsed.port:
        proxy["server"] += f":{parsed.port}"

    return proxy
