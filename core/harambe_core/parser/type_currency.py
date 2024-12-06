from pydantic import BeforeValidator
from typing import Union, Optional
from typing_extensions import Annotated
from harambe_core.parser.type_price import ParserTypePrice
from harambe_core.parser.currencies import all_currencies, price_not_available_phrases


class CurrencyParser:
    @staticmethod
    def parse_currency_amount(
        value: Union[str, float, int, None],
    ) -> Union[float, None]:
        return ParserTypePrice.validate_price(value)

    def __call__(
        self, value: Union[str, float, int, None]
    ) -> dict[str, Optional[Union[str, float]]]:
        if isinstance(value, (float, int)):
            return {"currency": None, "currency_symbol": None, "amount": float(value)}
        symbol = currency_name = amount = None
        if value is not None:
            value = str(value).strip()
            if value.lower() in price_not_available_phrases:
                return {"currency": None, "currency_symbol": None, "amount": None}
            for sym, curr in all_currencies:
                if sym in value or curr.lower() in value.lower():
                    currency_name = curr
                    symbol = sym
                    break
            value = value.replace(symbol, "").strip() if symbol else value
            amount = self.parse_currency_amount(value)

        return {"currency": currency_name, "currency_symbol": symbol, "amount": amount}


ParserTypeCurrency = Annotated[
    dict[str, Optional[Union[str, float]]], BeforeValidator(CurrencyParser())
]
