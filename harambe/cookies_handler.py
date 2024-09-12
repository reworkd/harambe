from harambe.types import Cookie
from datetime import datetime, timezone, timedelta


def fix_cookie(cookie: Cookie) -> Cookie:
    # Hardcode expiry to two days ahead
    cookie["expires"] = (datetime.now(tz=timezone.utc) + timedelta(days=2)).timestamp()
    return cookie
