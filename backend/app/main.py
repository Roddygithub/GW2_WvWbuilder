from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

import os
import logging
from typing import Dict

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.logging_config import setup_logging
from app.db.session import engine, Base
from app.core.cache import cache as redis_cache

# Create database tables
Base.metadata.create_all(bind=engine)


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="GW2 WvW Builder API - Optimize your WvW compositions for Guild Wars 2",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Initialize Redis cache on startup
    @application.on_event("startup")
    async def startup_event():
        """Initialize Redis cache on application startup."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing Redis cache...")
        try:
            await redis_cache.init_redis()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
    
    # Close Redis connection on shutdown
    @application.on_event("shutdown")
    async def shutdown_event():
        """Close Redis connection on application shutdown."""
        logger = logging.getLogger(__name__)
        logger.info("Closing Redis connection...")
        try:
            await redis_cache.close()
            logger.info("Redis connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Set up GZip compression for responses
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    # Set up session middleware
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=14 * 24 * 60 * 60,  # 14 days in seconds
    )

    # Add security headers middleware
    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Ajoute des en-têtes de sécurité de base aux réponses."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # La ligne ci-dessous est souvent utilisée, mais peut être redondante avec des CSP modernes.
        # response.headers["X-XSS-Protection"] = "1; mode=block"
        # Un Content-Security-Policy plus strict est généralement préférable.
        # response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
        return response


    # Include API routes
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Set up static files if present (skip in test envs without static dir)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_dir) or os.path.isdir("static"):
        application.mount("/static", StaticFiles(directory="static"), name="static")

    # Set up logging
    setup_logging()

    # Create database tables (in development)
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)

    # Add exception handlers
    @application.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body},
        )

    @application.exception_handler(500)
    async def internal_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Add health check endpoint
    @application.get("/health")
    async def health_check() -> Dict[str, str]:
        return {"status": "ok"}

    # Add root endpoint
    @application.get("/")
    async def root() -> Dict[str, str]:
        return {
            "message": "Welcome to the GW2 WvW Builder API",
            "docs": "/docs",
            "version": "0.1.0",
        }

    return application


app = create_application()

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Hello World"}

# This allows the application to be run directly with: python -m app.main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
