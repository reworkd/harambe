from typing import Final

ALL_CURRENCIES: Final[dict[str, str]] = {
    "د.م.": "MAD",  # Moroccan Dirham
    "د.إ": "AED",  # UAE Dirham
    "د.ك": "KWD",  # Kuwaiti Dinar
    "Bs.": "VEF",  # Venezuelan Bolivar
    "S/.": "PEN",  # Peruvian Sol
    "B/.": "PAB",  # Panamanian Balboa
    "NZ$": "NZD",  # New Zealand Dollar
    "HK$": "HKD",  # Hong Kong Dollar
    "A$": "AUD",  # Australian Dollar
    "C$": "CAD",  # Canadian Dollar
    "S$": "SGD",  # Singapore Dollar
    "R$": "BRL",  # Brazilian Real
    "Z$": "ZWL",  # Zimbabwean Dollar
    "kr.": "SEK",  # Swedish Krona
    "₽": "RUB",  # Russian Ruble
    "₺": "TRY",  # Turkish Lira
    "₩": "KRW",  # South Korean Won
    "₦": "NGN",  # Nigerian Naira
    "₫": "VND",  # Vietnamese Dong
    "₱": "PHP",  # Philippine Peso
    "₡": "CRC",  # Costa Rican Colón
    "₭": "LAK",  # Lao Kip
    "₮": "MNT",  # Mongolian Tugrik
    "₲": "PYG",  # Paraguayan Guarani
    "฿": "THB",  # Thai Baht
    "€": "EUR",  # Euro
    "₪": "ILS",  # Israeli Shekel
    "₹": "INR",  # Indian Rupee
    "৳": "BDT",  # Bangladeshi Taka
    "zł": "PLN",  # Polish Zloty
    "៛": "KHR",  # Cambodian Riel
    "kr": "NOK",  # Norwegian Krone
    "Kč": "CZK",  # Czech Koruna
    "RM": "MYR",  # Malaysian Ringgit
    "DH": "DZD",  # Algerian Dinar
    "Ft": "HUF",  # Hungarian Forint
    "MK": "MWK",  # Malawian Kwacha
    "MT": "MZN",  # Mozambican Metical
    "L": "RON",  # Romanian Leu
    "T": "KZT",  # Kazakhstani Tenge
    "VT": "VUV",  # Vanuatu Vatu
    "Q": "GTQ",  # Guatemalan Quetzal
    "R": "ZAR",  # South African Rand
    "£": "GBP",  # British Pound
    "¥": "JPY",  # Japanese Yen
    "ƒ": "ANG",  # Netherlands Antillean Guilder
    "$": "USD",  # US Dollar
    "CHF": "CHF",  # Swiss Franc
}

PRICE_NOT_AVAILABLE_PHRASES: Final[set[str]] = {
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
    "to be determined",
    "price unlisted",
    "pricing unavailable",
    "inquire for price",
    "quote required",
    "price on request",
    "contact us for price",
    "pricing to follow",
    "no price mentioned",
    "ask for price",
    "coming soon",
    "check in-store",
    "price withheld",
    "details upon request",
    "pricing later",
    "info required for pricing",
    "ask for details",
    "no price set",
    "price to follow",
    "call us for details",
    "pricing hidden",
    "check back for price",
    "price not specified",
    "price not determined",
}
