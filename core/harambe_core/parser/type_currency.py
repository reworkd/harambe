from pydantic import BeforeValidator
from typing import Union, Optional
from typing_extensions import Annotated
from harambe_core.parser.type_price import ParserTypePrice
from harambe_core.parser.currencies import ALL_CURRENCIES, PRICE_NOT_AVAILABLE_PHRASES


class CurrencyParser:
    def __call__(
        self, value: Union[str, float, int, None]
    ) -> Optional[dict[str, Optional[Union[str, float]]]]:
        if isinstance(value, (float, int)):
            return {"currency": None, "currency_symbol": None, "amount": float(value)}

        if value is None or self._is_price_not_available(value):
            return None

        value_str = str(value).strip()
        symbol, currency_name = self._identify_currency(value_str)
        amount = self._extract_amount(value_str, symbol)

        return {"currency": currency_name, "currency_symbol": symbol, "amount": amount}

    @staticmethod
    def _is_price_not_available(value: Union[str, float, int]) -> bool:
        return str(value).strip().lower() in PRICE_NOT_AVAILABLE_PHRASES

    @staticmethod
    def _identify_currency(value: str) -> tuple[Optional[str], Optional[str]]:
        for symbol, currency_name in ALL_CURRENCIES.items():
            if symbol in value or currency_name.lower() in value.lower():
                return symbol, currency_name
        return None, None

    @staticmethod
    def _extract_amount(value: str, symbol: Optional[str]) -> Optional[float]:
        if symbol:
            value = value.replace(symbol, "").strip()
        return ParserTypePrice.validate_price(value)


ParserTypeCurrency = Annotated[
    Optional[dict[str, Optional[Union[str, float]]]], BeforeValidator(CurrencyParser())
]
