from markdownify import MarkdownConverter

class HTMLToTextConverter(MarkdownConverter):
    """
    Custom converter to convert data from HTML to text

    Strip out standard markdown syntax like headings, em, strong, a, etc.
    Include footnotes in brackets
    """

    def convert_sup(self, el, text, convert_as_inline):
        return f"[{text}]"

    def convert_sub(self, el, text, convert_as_inline):
        return f"[{text}]"

    def convert_span(self, el, text, convert_as_inline):
        if el.get("class") and "sup" in el.get("class"):
            return f"[{text}]"
        if el.get("class") and "sub" in el.get("class"):
            return f"[{text}]"
        return text

    def convert_h1(self, el, text, convert_as_inline):
        return self.convert_p(el, text, convert_as_inline)

    def convert_h2(self, el, text, convert_as_inline):
        return self.convert_p(el, text, convert_as_inline)

    def convert_h3(self, el, text, convert_as_inline):
        return self.convert_p(el, text, convert_as_inline)

    def convert_h4(self, el, text, convert_as_inline):
        return self.convert_p(el, text, convert_as_inline)

    def convert_h5(self, el, text, convert_as_inline):
        return self.convert_p(el, text, convert_as_inline)

    def convert_h6(self, el, text, convert_as_inline):
        return self.convert_p(el, text, convert_as_inline)

    # Treat inline elements as spans
    def convert_strong(self, el, text, convert_as_inline):
        return self.convert_span(el, text, convert_as_inline)

    def convert_em(self, el, text, convert_as_inline):
        return self.convert_span(el, text, convert_as_inline)

    def convert_a(self, el, text, convert_as_inline):
        return self.convert_span(el, text, convert_as_inline)
