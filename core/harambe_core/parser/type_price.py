import re
from typing import Any, Optional, Union

from price_parser import Price
from pydantic import BeforeValidator
from typing_extensions import Annotated, Literal

from harambe_core.parser.constants import CURRENCY_MAP, PRICE_NOT_AVAILABLE_PHRASES
from harambe_core.parser.type_currency import ParserTypeCurrency

# this will capture only the amount
NUMBER_PATTERN = re.compile(r"-?.?\d[\d,-\.]*")

PriceOutputType = dict[
    Literal["currency", "raw_currency", "amount", "raw_price"],
    Optional[Union[str, float]],
]


class ParserTypePrice:
    def __new__(cls, required: bool = True) -> Any:
        validator = BeforeValidator(cls.validate_price)
        base = PriceOutputType

        return Annotated[
            base if required else base | None,
            validator,
        ]

    @staticmethod
    def validate_price(
        value: Union[str, float, int, None],
    ) -> Optional[PriceOutputType]:
        if isinstance(value, (float, int)):
            return {
                "currency": None,
                "raw_currency": None,
                "amount": float(value),
                "raw_price": str(value),
            }

        if not value or not (value_str := str(value).strip()):
            return None

        if ParserTypePrice._is_price_not_available(value_str):
            return None

        amount = ParserTypePrice._extract_amount(value_str)
        if not isinstance(amount, (float, int)):
            return amount

        # not using price.amount because it does not handle negative amounts yet
        price = Price.fromstring(value_str)
        currency_code = ParserTypePrice._get_currency_code(price.currency)
        return {
            "currency": currency_code,
            "raw_currency": price.currency,
            "amount": amount,
            "raw_price": value_str,
        }

    @staticmethod
    def _is_price_not_available(value: str) -> bool:
        return value.lower() in PRICE_NOT_AVAILABLE_PHRASES

    @staticmethod
    def _get_currency_code(value: str) -> Optional[str]:
        if not value:
            return None

        for key, currency_code in CURRENCY_MAP.items():
            if key.upper() == value.upper():
                return currency_code

        return None

    @staticmethod
    def _extract_amount(value: str) -> float | None | Any:
        match = NUMBER_PATTERN.findall(value)

        if len(match) != 1:
            raise ValueError("Multiple price amounts found")

        return ParserTypeCurrency.validate_currency(match[0])
