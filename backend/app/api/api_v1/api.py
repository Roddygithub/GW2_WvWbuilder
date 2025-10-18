from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    users,
    roles,
    professions,
    compositions,
    compositions_generate,
    auth,
    builds,
    teams,
    team_members,
    tags,
    health,
    metrics,
    gw2,
    dashboard,
    builder,
    optimizer,
    mode_splits,
    meta_evolution,
)

api_router = APIRouter()

# Include available API endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(
    professions.router, prefix="/professions", tags=["Professions"]
)
api_router.include_router(
    compositions.router, prefix="/compositions", tags=["Compositions"]
)
api_router.include_router(
    compositions_generate.router, prefix="/compositions", tags=["Compositions"]
)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(builds.router, prefix="/builds", tags=["Builds"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(
    team_members.router, prefix="/team-members", tags=["Team Members"]
)

# Include health check endpoint
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])

# Include metrics endpoints (admin only)
api_router.include_router(metrics.router, prefix="/metrics", tags=["Database Metrics"])

# Include GW2 endpoints
api_router.include_router(gw2.router, prefix="/gw2", tags=["GW2"])

# Include dashboard endpoints
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# Include builder/optimizer endpoints
api_router.include_router(builder.router, prefix="/builder", tags=["Builder"])
api_router.include_router(optimizer.router, tags=["Optimizer"])
api_router.include_router(
    mode_splits.router, prefix="/mode-splits", tags=["Mode Splits"]
)

# Include meta evolution endpoints (v4.3)
api_router.include_router(
    meta_evolution.router, prefix="/meta", tags=["Meta Evolution"]
)
