from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    users,
    roles,
    professions,
    compositions,
    auth,
    gw2_api,
    optimization
)

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(professions.router, prefix="/professions", tags=["Professions"])
api_router.include_router(compositions.router, prefix="/compositions", tags=["Compositions"])
api_router.include_router(gw2_api.router, prefix="/gw2", tags=["Guild Wars 2 API"])
api_router.include_router(optimization.router, prefix="/optimize", tags=["Optimization"])
