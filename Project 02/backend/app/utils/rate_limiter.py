"""
app/utils/rate_limiter.py — SlowAPI rate limiter configuration.

Trade-off: Using in-memory storage here (no Redis dependency for dev).
In production: swap `storage_uri` to "redis://redis:6379/0"
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function: rate-limit per client IP address
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    # storage_uri="redis://redis:6379/0",  # Uncomment for production
)
