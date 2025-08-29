from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    users,
    roles,
    professions,
    compositions,
    auth,
)

api_router = APIRouter()

# Include available API endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(professions.router, prefix="/professions", tags=["Professions"])
api_router.include_router(compositions.router, prefix="/compositions", tags=["Compositions"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
