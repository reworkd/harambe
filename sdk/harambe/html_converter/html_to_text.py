from bs4.element import Tag
from markdownify import MarkdownConverter


class HTMLToTextConverter(MarkdownConverter):
    """
    Custom converter to convert data from HTML to text

    Strip out standard markdown syntax like headings, em, strong, a, etc.
    Include footnotes in brackets
    """

    def convert_sup(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return f"[{text}]"

    def convert_sub(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return f"[{text}]"

    def convert_span(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        if el.get("class") and "sup" in el.get("class"):
            return f"[{text}]"
        if el.get("class") and "sub" in el.get("class"):
            return f"[{text}]"
        return text

    # Remove markdown headings
    def convert_h1(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_p(el, text, convert_as_inline)

    def convert_h2(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_p(el, text, convert_as_inline)

    def convert_h3(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_p(el, text, convert_as_inline)

    def convert_h4(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_p(el, text, convert_as_inline)

    def convert_h5(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_p(el, text, convert_as_inline)

    def convert_h6(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_p(el, text, convert_as_inline)

    # Treat inline elements as spans
    def convert_strong(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_span(el, text, convert_as_inline)

    def convert_em(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_span(el, text, convert_as_inline)

    def convert_a(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        return self.convert_span(el, text, convert_as_inline)
