"""Health check endpoints for the API."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db

router = APIRouter()


@router.get("/health", status_code=200, tags=["health"])
async def health_check(db: AsyncSession = Depends(get_async_db)) -> JSONResponse:
    """
    Health check endpoint.
    
    Returns:
        JSONResponse: A simple status message indicating the API is running.
    """
    # Test database connection
    try:
        # Execute a simple query to verify database connectivity
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "database": db_status,
            "version": "1.0.0"
        }
    )
