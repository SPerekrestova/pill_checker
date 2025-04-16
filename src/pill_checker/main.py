from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.pill_checker.app.api.v1 import auth
from src.pill_checker.app.api.v1 import medications
from src.pill_checker.app.core.config import settings
from src.pill_checker.app.core.events import setup_events
from src.pill_checker.app.core.security import setup_security

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API for PillChecker application",
    docs_url="/api/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure static files and templates
static_dir = Path("app/static")
templates = Jinja2Templates(directory=Path("app/templates"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure security and events
setup_security(app)
setup_events(app)


# Basic routes
@app.get("/")
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("base.html", {"request": request, "user": None})


@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon."""
    return FileResponse(static_dir / "img/favicon.svg", media_type="image/svg+xml")


# Health check endpoint for Docker
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Auth routes
@app.get("/login")
async def login_page(request: Request):
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request, "user": None})


@app.get("/register")
async def register_page(request: Request):
    """Render the registration page."""
    return templates.TemplateResponse(
        "register.html", {"request": request, "user": None}
    )


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


@app.get("/medication/{medication_id}")
async def medication_detail_page(request: Request, medication_id: int):
    """Render the medication detail page."""
    # TODO: Add authentication middleware
    return templates.TemplateResponse(
        "medication_detail.html",
        {
            "request": request,
            "user": {"email": "test@example.com"},  # Placeholder user data
            "medication_id": medication_id,
        },
    )


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

app.include_router(
    medications.router,
    prefix=f"{settings.API_V1_STR}/medications",
    tags=["medications"],
)
