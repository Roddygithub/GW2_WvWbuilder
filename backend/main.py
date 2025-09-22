from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings


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

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

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
