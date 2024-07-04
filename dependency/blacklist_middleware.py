from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .blacklist import is_banned, temporary_blacklist_ip, permanent_blacklist_ip
from cache.connection import redis_client


async def blacklist_middleware(request: Request, call_next):
    ip = request.client.host

    # Check if the IP is permanently blacklisted
    if redis_client.get(f"blacklist_{ip}"):
        return JSONResponse(status_code=403, content={"detail": "Your IP is permanently blacklisted for 5 minutes."})

    # Check if the IP is temporarily blacklisted
    if redis_client.get(f"temp_blacklist_{ip}"):
        return JSONResponse(status_code=403, content={"detail": "Your IP is temporarily blacklisted for 1 minute."})

    # Increment request count
    request_count = redis_client.incr(f"request_count_{ip}")

    # Check if request count exceeds limit
    if request_count > 5:
        # Check if the IP was previously temporarily blacklisted
        if redis_client.get(f"was_temp_blacklisted_{ip}"):
            permanent_blacklist_ip(ip)
            return JSONResponse(status_code=403, content={
                "detail": "Too many requests, your IP is now permanently blacklisted for 5 minutes."})

        # Temporarily blacklist the IP
        temporary_blacklist_ip(ip)
        redis_client.set(f"was_temp_blacklisted_{ip}", "1",
                               ex=300)  # Keep track of the temp blacklist status for 5 minutes
        return JSONResponse(status_code=403,
                            content={"detail": "Too many requests, your IP is temporarily blacklisted for 1 minute."})

    response = await call_next(request)

    # Reset request count after 60 seconds
    redis_client.expire(f"request_count_{ip}", 60)

    return response
