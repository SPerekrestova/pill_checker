"""Security configuration and middleware for the application."""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp

from .config import settings

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Rate limiting configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{settings.RATE_LIMIT_PER_SECOND} per second",
        f"{settings.RATE_LIMIT_PER_MINUTE} per minute",
        f"{settings.RATE_LIMIT_PER_HOUR} per hour",
    ],
)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> Response:
    """Handle rate limit exceeded errors."""
    return Response(
        status_code=429,
        content="Too many requests. Please try again later.",
        media_type="text/plain",
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""

    def __init__(
        self,
        app: ASGIApp,
        hsts: bool = True,
        xfo: str = "DENY",
        include_dev_headers: bool = False,
    ) -> None:
        super().__init__(app)
        self.hsts = hsts
        self.xfo = xfo
        self.include_dev_headers = include_dev_headers

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = self.xfo
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers[
            "Permissions-Policy"
        ] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "img-src 'self' data: https:",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:",
            "style-src 'self' 'unsafe-inline' https:",
            "font-src 'self' https:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests",
            "block-all-mixed-content",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # HSTS (only in production)
        if self.hsts and not settings.DEBUG:
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains; preload"

        return response


def setup_security(app: FastAPI) -> None:
    """Configure security middleware and CORS."""

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "Range"],
        max_age=3600,
    )

    # Session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=86400,  # 1 day
        same_site="lax",
        path="/",  # Cookie path
    )

    # Security headers middleware
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts=not settings.DEBUG,
        include_dev_headers=settings.DEBUG,
    )

    # Trusted hosts middleware (only in production)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[str(host) for host in settings.TRUSTED_HOSTS],
        )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
