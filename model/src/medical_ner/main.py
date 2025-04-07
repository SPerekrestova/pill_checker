import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from medical_ner.core.logging import configure_logging

from .api.router import router
from .core.config import settings
from .services.nlp import get_nlp_model
from fastapi import Request
import time

# Configure logging before anything else
configure_logging()
logger = logging.getLogger(__name__)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload the model at startup
    try:
        get_nlp_model()
        logger.info("Model preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload model: {e}")
    yield


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        lifespan=lifespan,
        title="Medical NER Service",
        description="A service for medical named entity recognition and linking",
        version="0.1.0",
        debug=settings.DEBUG,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Specify allowed origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routers
    app.include_router(router, prefix=settings.API_PREFIX)

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "medical_ner.main:app", host="0.0.0.0", port=8081, reload=settings.DEBUG
    )
