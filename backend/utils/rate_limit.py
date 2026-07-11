import asyncio
from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request, status

_requests: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_lock = asyncio.Lock()


async def enforce_rate_limit(scope: str, key_value: str, limit: int, window_seconds: int) -> None:
    key = (scope, key_value)
    now = monotonic()

    async with _lock:
        if len(_requests) > 10_000:
            stale_before = now - max(window_seconds, 3600)
            stale_keys = [item_key for item_key, values in _requests.items() if not values or values[-1] < stale_before]
            for stale_key in stale_keys:
                _requests.pop(stale_key, None)
        bucket = _requests[key]
        while bucket and bucket[0] <= now - window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={"Retry-After": str(window_seconds)},
            )
        bucket.append(now)


def rate_limit(scope: str, limit: int, window_seconds: int):
    async def check(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        await enforce_rate_limit(scope, client_ip, limit, window_seconds)

    return check
