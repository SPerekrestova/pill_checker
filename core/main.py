from app.api.v1 import auth, medications
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.logging_config import logger

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME, version="1.0.0", description="API for PillChecker application"
)

# Configure static files and templates
static_dir = Path("app/static")
templates = Jinja2Templates(directory=Path("app/templates"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=86400,  # 1 day
    https_only=True,
    same_site="lax",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection test
@app.on_event("startup")
async def startup_event() -> None:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Connected to database. PostgreSQL version: {version}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


# Basic routes
@app.get("/")
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("base.html", {"request": request, "user": None})


@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon."""
    return FileResponse(static_dir / "img/favicon.svg", media_type="image/svg+xml")


# Auth routes
@app.get("/login")
async def login_page(request: Request):
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request, "user": None})


@app.get("/register")
async def register_page(request: Request):
    """Render the registration page."""
    return templates.TemplateResponse("register.html", {"request": request, "user": None})


@app.get("/dashboard")
async def dashboard_page(request: Request):
    """Render the dashboard page (protected route)."""
    # TODO: Add authentication middleware
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": {"email": "test@example.com"},  # Placeholder user data
            "medications": [],  # Empty list for now
        },
    )


# Include API routers

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

app.include_router(
    medications.router, prefix=f"{settings.API_V1_STR}/medications", tags=["medications"]
)

if __name__ == "__main__":
    import uvicorn

    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Accessible from outside the container
        port=8000,
        reload=True,  # Enable auto-reload
        workers=1,  # Single worker for development
        log_level="info",
    )
