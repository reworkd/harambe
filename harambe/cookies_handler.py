from harambe.types import Cookie
from datetime import datetime, timezone, timedelta


def fix_cookie(cookie: Cookie) -> Cookie:
    """
    Fix the cookie expiry by setting it to one day ahead only if it's expiring within a day.

    :param cookie: The cookie to modify.
    :return: The modified cookie.
    """
    current_time = datetime.now(tz=timezone.utc)
    if "expires" in cookie:
        expiry_time = datetime.fromtimestamp(cookie["expires"], tz=timezone.utc)
        if (expiry_time - current_time) < timedelta(days=1):
            cookie["expires"] = (current_time + timedelta(days=1)).timestamp()
    else:
        cookie["expires"] = (current_time + timedelta(days=1)).timestamp()

    return cookie
