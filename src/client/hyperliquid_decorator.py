from functools import wraps

from core.exceptions import PriceRestrictedException


def handle_order_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            if "Cannot place order" in error_message and "more aggressive than oracle when open interest is at cap" in error_message:
                raise PriceRestrictedException("too aggressive price with capped OI")
            raise
    return wrapper
