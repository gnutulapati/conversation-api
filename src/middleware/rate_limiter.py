from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Global limiter instance
limiter = Limiter(key_func=get_remote_address)

def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles 429 Too Many Requests errors.
    """
    return _rate_limit_exceeded_handler(request, exc)
