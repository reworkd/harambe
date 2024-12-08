from typing import Literal

from harambe.html_converter.html_to_markdown import HTMLToMarkdownConverter
from harambe.html_converter.html_to_text import HTMLToTextConverter
from harambe_core.errors import UnknownHTMLConverter
from markdownify import MarkdownConverter

HTMLConverterType = Literal["markdown", "text"]


def get_html_converter(
    html_converter_type: HTMLConverterType,
) -> MarkdownConverter:
    if html_converter_type == "markdown":
        return HTMLToMarkdownConverter()
    elif html_converter_type == "text":
        return HTMLToTextConverter()

    raise UnknownHTMLConverter(html_converter_type)
