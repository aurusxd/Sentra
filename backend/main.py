from fastapi import Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from backend.api.routers import create_app
from backend.core.jwt import get_jwt_key
from backend.utils.toeken_crypto import get_fernet

get_jwt_key()
get_fernet()

app = create_app()

ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://sentra.fun",
    "https://www.sentra.fun",
}


@app.middleware("http")
async def reject_untrusted_browser_origins(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method not in {"GET", "HEAD", "OPTIONS"} and origin and origin not in ALLOWED_ORIGINS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Untrusted request origin"},
        )
    return await call_next(request)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.sentra.fun", "sentra.fun", "www.sentra.fun", "localhost", "127.0.0.1", "backend", "testserver"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
