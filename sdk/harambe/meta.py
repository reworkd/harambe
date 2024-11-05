import ast
from pathlib import Path
from typing import List, TypedDict, cast
from urllib.parse import urlparse


class DecoratedScraper(TypedDict):
    file_path: str
    function_name: str
    domain: str
    stage: str
    package: str


def is_sdk_scraper_decorator(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "scraper"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "SDK"
    )


def find_decorated_scrapers(file_path: Path) -> List[DecoratedScraper]:
    with open(file_path, "r") as source:
        node = ast.parse(source.read())

    decorated_methods: List[DecoratedScraper] = []
    for func in [n for n in node.body if isinstance(n, ast.AsyncFunctionDef)]:
        for decorator in func.decorator_list:
            if is_sdk_scraper_decorator(decorator):
                decorator = cast(ast.Call, decorator)
                kws = {kw.arg: kw.value.s for kw in decorator.keywords}  # type: ignore
                domain = kws["domain"]

                decorated_methods.append(
                    {
                        "file_path": str(file_path),
                        "function_name": func.name,
                        "domain": domain,
                        "stage": kws["stage"],
                        "package": url_to_package(domain),
                    }
                )

    return decorated_methods


def walk_package_for_decorators(path: Path) -> List[DecoratedScraper]:
    files = (
        [path]
        if path.is_file()
        else [p for p in path.rglob("*.py") if not p.name.startswith("_")]
    )

    decorated_methods_in_package = []
    for file in files:
        decorated_methods_in_package.extend(find_decorated_scrapers(file))

    return decorated_methods_in_package


def url_to_netloc(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    domain = urlparse(url).netloc
    domain = domain.split(":")[0]
    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def url_to_package(url: str) -> str:
    domain = url_to_netloc(url)

    parts = domain.split(".")
    reversed_parts = parts[::-1]

    package_name = ".".join(reversed_parts)
    return package_name
