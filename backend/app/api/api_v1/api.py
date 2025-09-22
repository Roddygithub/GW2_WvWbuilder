from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    users,
    roles,
    professions,
    compositions,
    auth,
<<<<<<< HEAD
    builds
=======
    builds,
    teams,
    team_members,
    tags,
>>>>>>> a023051 (feat: optimized CRUD with Redis caching + full test coverage + docs and monitoring guide)
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
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
<<<<<<< HEAD
api_router.include_router(builds.router, prefix="/builds", tags=["builds"])
=======
api_router.include_router(builds.router, prefix="/builds", tags=["Builds"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(
    team_members.router, 
    prefix="/teams",  # Les routes commencent par /teams/{team_id}/members
    tags=["Team Members"]
)
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
>>>>>>> a023051 (feat: optimized CRUD with Redis caching + full test coverage + docs and monitoring guide)
