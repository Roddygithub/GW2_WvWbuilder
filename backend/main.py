from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

import logging
import time

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.limiter import init_rate_limiter, close_rate_limiter


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add Prometheus instrumentation
    Instrumentator().instrument(app).expose(app)

    # Initialize app rate limiter on startup and close on shutdown
    @app.on_event("startup")
    async def startup():
        await init_rate_limiter()

    @app.on_event("shutdown")
    async def shutdown():
        await close_rate_limiter()

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger = logging.getLogger("uvicorn.access")
        logger.info(f"Incoming Request: {request.method} {request.url}")
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Outgoing Response: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Add GZip compression for responses
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Serve static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


# Create the FastAPI application
app = create_application()


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to GW2 WvW Builder API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
