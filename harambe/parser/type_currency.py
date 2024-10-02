from pydantic import BeforeValidator
from typing import Any
import re
from typing_extensions import Annotated

price_not_available_phrases = {
    "price not available",
    "unavailable price",
    "price upon request",
    "contact for price",
    "request a quote",
    "call for price",
    "check price in store",
    "price tbd",
    "price not disclosed",
    "out of stock",
    "sold out",
    "pricing not provided",
    "not priced",
    "currently unavailable",
    "n/a",
    "ask for pricing",
    "see details for price",
    "price coming soon",
    "temporarily unavailable",
    "price hidden",
    "tdb",
}

currency_symbols = {
    "$",
    "€",
    "£",
    "¥",
    "₹",
    "₽",
    "₩",
    "₫",
    "₴",
    "₦",
    "₪",
    "₱",
    "฿",
    "₲",
    "₭",
    "₵",
    "₡",
    "₸",
    "₺",
    "ƒ",
    "₳",
    "₼",
    "₢",
    "₣",
    "₥",
    "₯",
    "₠",
    "₧",
    "₰",
}


class ParserTypeCurrency:
    def __new__(cls) -> Any:
        return Annotated[str | None, BeforeValidator(cls.validate_currency)]

    @staticmethod
    def validate_currency(value: str) -> str | None:
        if isinstance(value, (float, int)):
            return str(float(value))

        value = str(value).strip().lower()

        if value in price_not_available_phrases:
            return None

        currency_symbol = next(
            (symbol for symbol in currency_symbols if symbol in value), ""
        )

        cleaned_value = re.sub(r"[^\d.,-]", "", value)
        cleaned_value = cleaned_value.lstrip("0")

        if "." in cleaned_value:
            parts = cleaned_value.split(".")
            if len(parts[-1]) == 3:
                cleaned_value = cleaned_value.replace(".", "")

        if cleaned_value.startswith("."):
            cleaned_value = "0" + cleaned_value

        if "," in cleaned_value:
            if "." in cleaned_value:
                if cleaned_value.index(",") < cleaned_value.index("."):
                    cleaned_value = cleaned_value.replace(",", "")
                else:
                    cleaned_value = cleaned_value.replace(".", "").replace(",", ".")
            else:
                if len(cleaned_value.split(",")[-1]) == 3:
                    cleaned_value = cleaned_value.replace(",", "")
                else:
                    cleaned_value = cleaned_value.replace(",", ".")

        if cleaned_value.startswith("-"):
            return "-" + currency_symbol + str(float(cleaned_value[1:].strip()))

        return currency_symbol + str(float(cleaned_value.strip()))
