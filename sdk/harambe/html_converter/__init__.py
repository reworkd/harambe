from typing import Literal

from harambe_core.errors import UnknownHTMLConverter
from markdownify import MarkdownConverter

from sdk.harambe.html_converter.html_to_markdown import HTMLToMarkdownConverter
from sdk.harambe.html_converter.html_to_text import HTMLToTextConverter

HTMLConverterType = Literal["markdown", "text"]


def get_html_converter(
    html_converter_type: HTMLConverterType | None,
) -> MarkdownConverter:
    if html_converter_type == "markdown":
        return HTMLToMarkdownConverter()
    if html_converter_type == "text":
        return HTMLToTextConverter()
    else:
        raise UnknownHTMLConverter(html_converter_type)
