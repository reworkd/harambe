all_currencies = sorted(
    [
        ("$", "USD"),  # US Dollar
        ("€", "EUR"),  # Euro
        ("¥", "JPY"),  # Japanese Yen
        ("£", "GBP"),  # British Pound
        ("A$", "AUD"),  # Australian Dollar
        ("C$", "CAD"),  # Canadian Dollar
        ("CHF", "CHF"),  # Swiss Franc
        ("¥", "CNY"),  # Chinese Yuan
        ("kr.", "SEK"),  # Swedish Krona
        ("NZ$", "NZD"),  # New Zealand Dollar
        ("S$", "SGD"),  # Singapore Dollar
        ("HK$", "HKD"),  # Hong Kong Dollar
        ("kr", "NOK"),  # Norwegian Krone
        ("₩", "KRW"),  # South Korean Won
        ("₺", "TRY"),  # Turkish Lira
        ("₹", "INR"),  # Indian Rupee
        ("₽", "RUB"),  # Russian Ruble
        ("R$", "BRL"),  # Brazilian Real
        ("R", "ZAR"),  # South African Rand
        ("RM", "MYR"),  # Malaysian Ringgit
        ("฿", "THB"),  # Thai Baht
        ("Rp", "IDR"),  # Indonesian Rupiah
        ("zł", "PLN"),  # Polish Zloty
        ("₱", "PHP"),  # Philippine Peso
        ("Kč", "CZK"),  # Czech Koruna
        ("د.إ", "AED"),  # UAE Dirham
        ("Ft", "HUF"),  # Hungarian Forint
        ("₪", "ILS"),  # Israeli Shekel
        ("﷼", "SAR"),  # Saudi Riyal
        ("₦", "NGN"),  # Nigerian Naira
        ("د.ك", "KWD"),  # Kuwaiti Dinar
        ("B/.", "PAB"),  # Panamanian Balboa
        ("kr", "DKK"),  # Danish Krone
        ("S/.", "PEN"),  # Peruvian Sol
        ("₲", "PYG"),  # Paraguayan Guarani
        ("$", "MXN"),  # Mexican Peso
        ("Q", "GTQ"),  # Guatemalan Quetzal
        ("Bs.", "VEF"),  # Venezuelan Bolivar
        ("$", "ARS"),  # Argentine Peso
        ("$", "CLP"),  # Chilean Peso
        ("$", "COP"),  # Colombian Peso
        ("₡", "CRC"),  # Costa Rican Colón
        ("د.م.", "MAD"),  # Moroccan Dirham
        ("DH", "DZD"),  # Algerian Dinar
        ("T", "KZT"),  # Kazakhstani Tenge
        ("лв", "BGN"),  # Bulgarian Lev
        ("L", "RON"),  # Romanian Leu
        ("$", "TTD"),  # Trinidad and Tobago Dollar
        ("ƒ", "ANG"),  # Netherlands Antillean Guilder
        ("₭", "LAK"),  # Lao Kip
        ("₮", "MNT"),  # Mongolian Tugrik
        ("VT", "VUV"),  # Vanuatu Vatu
        ("K", "PGK"),  # Papua New Guinean Kina
        ("៛", "KHR"),  # Cambodian Riel
        ("MK", "MWK"),  # Malawian Kwacha
        ("MT", "MZN"),  # Mozambican Metical
        ("Z$", "ZWL"),  # Zimbabwean Dollar
        ("₫", "VND"),  # Vietnamese Dong
        ("৳", "BDT"),  # Bangladeshi Taka
    ],
    key=lambda x: len(x[0]),
    reverse=True,
)

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
