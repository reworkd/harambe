import pytest

from harambe.normalize_url import normalize_url, sanitize_scheme


@pytest.mark.parametrize(
    "base_path, url, expected",
    [
        (
            "https://example.com/subdir/page.html",
            "/x/X/picture.png",
            "https://example.com/x/X/picture.png",
        ),
        (
            "https://example.com/subdir/page.html",
            "./../x/X/picture.png",
            "https://example.com/x/X/picture.png",
        ),
        (
            "https://example.com/",
            "https://example.com/x/X/picture.png",
            "https://example.com/x/X/picture.png",
        ),
        ("https://example.com/subdir/", "", "https://example.com/subdir/"),
        (
            "https://example.com/",
            "/x/X/picture.png?query=123#fragment",
            "https://example.com/x/X/picture.png?query=123#fragment",
        ),
        (
            "https://example.com/subdir/",
            "./../../x/X/picture.png",
            "https://example.com/x/X/picture.png",
        ),
        (
            "https://example.com/subdir/",
            "./img/picture.png",
            "https://example.com/subdir/img/picture.png",
        ),
        (
            "https://example.com/subdir/page.html/",
            "/x/X/picture.png?query=123#fragment",
            "https://example.com/x/X/picture.png?query=123#fragment",
        ),
        (
            "https://example.com/subdir/page.html",
            "https:/www.reestrnpa.gov.ua/REESTR/RNAweb.nsf/wpage/doc_card?OpenDocument&ID=689A2315F9D6C1D7C22587CF004A5E58",
            "https://www.reestrnpa.gov.ua/REESTR/RNAweb.nsf/wpage/doc_card?OpenDocument&ID=689A2315F9D6C1D7C22587CF004A5E58",
        ),
        (
            "https://example.com/subdir/page.html",
            "https://confetti.dev",
            "https://confetti.dev",
        ),
        (
            "example.com",
            "/test",
            "https://example.com/test",
        ),
        (
            "https://www.eeaa.gov.eg/Laws/58/index",
            R"https://www.eeaa.gov.eg\Uploads/Laws/Files\20221018140838825.pdf",
            "https://www.eeaa.gov.eg/Uploads/Laws/Files/20221018140838825.pdf",
        ),
        (
            # Base HTTP and link HTTPS
            "http://example.com",
            "https://example.com/image.png",
            "https://example.com/image.png",
        ),
        (
            # Base and link HTTP
            "http://example.com",
            "http://example.com/image.png",
            "http://example.com/image.png",
        ),
        (
            # Base HTTPS and link HTTP
            "https://example.com",
            "http://example.com/image.png",
            "http://example.com/image.png",
        ),
        (
            # Normalizing artifacts from not joining urls properly
            "https://evp.nc.gov/",
            "https://evp.nc.gov//solicitations/details/?id=a4382140-25b6-ee11-a569-001dd804ec4b",
            "https://evp.nc.gov/solicitations/details/?id=a4382140-25b6-ee11-a569-001dd804ec4b",
        ),
        (
            "https://www.bidbuy.illinois.gov/bso/view/search/external/advancedSearchBid.xhtml?openBids=true",
            "/bso/external/bidDetail.sdo?docId=24-497DVA-MANTE-B-41187&external=true&parentUrl=close",
            "https://www.bidbuy.illinois.gov/bso/external/bidDetail.sdo?docId=24-497DVA-MANTE-B-41187&external=true&parentUrl=close",
        ),
        (
            "https://www.bidbuy.illinois.gov/bso/view/search/external/advancedSearchBid.xhtml?openBids=true",
            "//example.com",
            "https://example.com",
        ),
    ],
)
def test_normalize_url(base_path, url, expected):
    assert normalize_url(url, base_path) == expected


@pytest.mark.parametrize(
    "input_url, expected_url",
    [
        ("http://example.com", "http://example.com"),
        ("https://example.com", "https://example.com"),
        ("http:/example.com", "http://example.com"),
        ("https:/example.com", "https://example.com"),
        ("https/example.com", "https/example.com"),
        ("www.example.com", "www.example.com"),
    ],
)
def test_sanitize_scheme(input_url, expected_url):
    assert sanitize_scheme(input_url) == expected_url