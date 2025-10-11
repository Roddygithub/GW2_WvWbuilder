from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    users,
    roles,
    professions,
    compositions,
    auth,
    builds,
    teams,
    team_members,
    tags,
    health,
    metrics,
    gw2,
)

api_router = APIRouter()

# Include available API endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(professions.router, prefix="/professions", tags=["Professions"])
api_router.include_router(compositions.router, prefix="/compositions", tags=["Compositions"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(builds.router, prefix="/builds", tags=["Builds"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(team_members.router, prefix="/team-members", tags=["Team Members"])

# Include health check endpoint
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])

# Include metrics endpoints (admin only)
api_router.include_router(metrics.router, prefix="/metrics", tags=["Database Metrics"])

# Include GW2 endpoints
api_router.include_router(gw2.router, prefix="/gw2", tags=["GW2"])
