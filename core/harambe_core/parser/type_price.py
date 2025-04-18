import re
from typing import Any, Optional, Union

from price_parser import Price
from pydantic import BeforeValidator
from typing_extensions import Annotated, Literal

from harambe_core.parser.constants import CURRENCY_MAP, PRICE_NOT_AVAILABLE_PHRASES
from harambe_core.parser.type_currency import ParserTypeCurrency

# this will capture only the amount
number_pattern = re.compile(r"-?.?\d[\d,-\.]*")


class ParserTypePrice:
    def __new__(cls, required: bool = True) -> Any:
        validator = BeforeValidator(cls.validate_price)
        base = dict[
            Literal["currency", "currency_raw", "amount", "raw_price"],
            Optional[Union[str, float]],
        ]

        return Annotated[
            base if required else base | None,
            validator,
        ]

    @staticmethod
    def validate_price(
        value: Union[str, float, int, None],
    ) -> Optional[
        dict[
            Literal["currency", "currency_raw", "amount", "raw_price"],
            Optional[Union[str, float]],
        ]
    ]:
        if isinstance(value, (float, int)):
            return {
                "currency": None,
                "currency_raw": None,
                "amount": float(value),
                "raw_price": str(value),
            }

        if not value or ParserTypePrice._is_price_not_available(value):
            return None

        value_str = str(value).strip()
        amount = ParserTypePrice._extract_amount(value_str)
        if amount is None:
            return None
        # not using price.amount because it does not handle negative amounts yet
        price = Price.fromstring(value_str)
        currency_code = ParserTypePrice._identify_currency(price.currency)
        return {
            "currency": currency_code,
            "currency_raw": price.currency,
            "amount": amount,
            "raw_price": value_str,
        }

    @staticmethod
    def _is_price_not_available(value: Union[str, float, int]) -> bool:
        return str(value).strip().lower() in PRICE_NOT_AVAILABLE_PHRASES

    @staticmethod
    def _identify_currency(value: str) -> Optional[str]:
        if not value:
            return None
        for symbol, currency_code in CURRENCY_MAP.items():
            if symbol.upper() == value.upper():
                return currency_code
        return None

    @staticmethod
    def _extract_amount(value: str) -> Optional[float]:
        match = number_pattern.findall(value)

        if len(match) != 1:
            raise ValueError("Multiple price amounts found")

        return ParserTypeCurrency.validate_currency(match[0])
