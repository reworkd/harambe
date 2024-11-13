from pydantic import BeforeValidator
from typing import Union, Optional
from typing_extensions import Annotated
from harambe_core.parser.type_price import ParserTypePrice

popular_currencies = sorted(
    [
        ("$", "USD"),
        ("€", "EUR"),
        ("¥", "JPY"),
        ("£", "GBP"),
        ("A$", "AUD"),
        ("C$", "CAD"),
        ("CHF", "CHF"),
        ("¥", "CNY"),
        ("kr", "SEK"),
        ("NZ$", "NZD"),
        ("S$", "SGD"),
        ("HK$", "HKD"),
        ("kr", "NOK"),
        ("₩", "KRW"),
        ("₺", "TRY"),
        ("₹", "INR"),
        ("₽", "RUB"),
        ("R$", "BRL"),
        ("R", "ZAR"),
        ("RM", "MYR"),
        ("฿", "THB"),
        ("Rp", "IDR"),
        ("zł", "PLN"),
        ("₱", "PHP"),
        ("Kč", "CZK"),
        ("د.إ", "AED"),
        ("Ft", "HUF"),
        ("₪", "ILS"),
        ("﷼", "SAR"),
    ],
    key=lambda x: len(x[0]),
    reverse=True,
)


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
        amount = self.parse_currency_amount(value)
        symbol = None
        currency_name = None
        if amount is not None:
            for sym, curr in popular_currencies:
                if sym in value or curr in value:
                    currency_name = curr
                    symbol = sym
                    break

        return {"currency": currency_name, "currency_symbol": symbol, "amount": amount}


ParserTypeCurrency = Annotated[
    dict[str, Optional[Union[str, float]]], BeforeValidator(CurrencyParser())
]
