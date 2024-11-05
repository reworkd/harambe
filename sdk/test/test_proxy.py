import pytest

from harambe.proxy import proxy_from_url


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "http://user:pass@hostname:8080",
            {"server": "hostname:8080", "username": "user", "password": "pass"},
        ),
        (
            "user:pass@hostname:8080",
            {"server": "hostname:8080", "username": "user", "password": "pass"},
        ),
        (
            "http://user:pass@hostname",
            {"server": "hostname", "username": "user", "password": "pass"},
        ),
        (
            "user:pass@hostname",
            {"server": "hostname", "username": "user", "password": "pass"},
        ),
    ],
)
def test_proxy_from_url_valid(url, expected):
    assert proxy_from_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "http://hostname:8080",
        "hostname:8080",
        "http://user@hostname:8080",
        "user@hostname:8080",
        "http://hostname",
        "hostname",
    ],
)
def test_proxy_from_url_invalid(url):
    with pytest.raises(ValueError):
        proxy_from_url(url)
