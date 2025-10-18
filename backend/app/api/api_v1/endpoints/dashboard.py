"""
Dashboard endpoints for user statistics and recent activity
"""

from typing import Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import dependencies as deps

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics schema"""

    total_compositions: int = 0
    total_builds: int = 0
    total_teams: int = 0
    recent_activity_count: int = 0


class RecentActivity(BaseModel):
    """Recent activity schema"""

    id: str
    type: str  # 'composition', 'build', 'team', 'tag'
    title: str
    description: str
    timestamp: str


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get dashboard statistics for the current user.
    """
    # Count user's compositions
    compositions_stmt = select(func.count(models.Composition.id)).where(
        models.Composition.created_by == current_user.id
    )
    compositions_result = await db.execute(compositions_stmt)
    total_compositions = compositions_result.scalar() or 0

    # Count user's builds
    builds_stmt = select(func.count(models.Build.id)).where(
        models.Build.created_by_id == current_user.id
    )
    builds_result = await db.execute(builds_stmt)
    total_builds = builds_result.scalar() or 0

    # Count user's teams
    teams_stmt = select(func.count(models.Team.id)).where(
        models.Team.owner_id == current_user.id
    )
    teams_result = await db.execute(teams_stmt)
    total_teams = teams_result.scalar() or 0

    # Count recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_compositions_stmt = select(func.count(models.Composition.id)).where(
        models.Composition.created_by == current_user.id,
        models.Composition.created_at >= thirty_days_ago,
    )
    recent_result = await db.execute(recent_compositions_stmt)
    recent_activity_count = recent_result.scalar() or 0

    return DashboardStats(
        total_compositions=total_compositions,
        total_builds=total_builds,
        total_teams=total_teams,
        recent_activity_count=recent_activity_count,
    )


@router.get("/activities", response_model=List[RecentActivity])
async def get_recent_activities(
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get recent activities for the current user.
    Returns a list of recent compositions, builds, and teams.
    """
    activities: List[RecentActivity] = []

    # Get recent compositions
    compositions_stmt = (
        select(models.Composition)
        .where(models.Composition.created_by == current_user.id)
        .order_by(models.Composition.created_at.desc())
        .limit(limit)
    )
    compositions_result = await db.execute(compositions_stmt)
    compositions = compositions_result.scalars().all()

    for comp in compositions:
        activities.append(
            RecentActivity(
                id=f"comp-{comp.id}",
                type="composition",
                title=f"Created composition: {comp.name}",
                description=comp.description or "No description",
                timestamp=(
                    comp.created_at.isoformat()
                    if comp.created_at
                    else datetime.utcnow().isoformat()
                ),
            )
        )

    # Get recent builds
    builds_stmt = (
        select(models.Build)
        .where(models.Build.created_by_id == current_user.id)
        .order_by(models.Build.created_at.desc())
        .limit(limit)
    )
    builds_result = await db.execute(builds_stmt)
    builds = builds_result.scalars().all()

    for build in builds:
        activities.append(
            RecentActivity(
                id=f"build-{build.id}",
                type="build",
                title=f"Created build: {build.name}",
                description=build.description or "No description",
                timestamp=(
                    build.created_at.isoformat()
                    if build.created_at
                    else datetime.utcnow().isoformat()
                ),
            )
        )

    # Get recent teams
    teams_stmt = (
        select(models.Team)
        .where(models.Team.owner_id == current_user.id)
        .order_by(models.Team.created_at.desc())
        .limit(limit)
    )
    teams_result = await db.execute(teams_stmt)
    teams = teams_result.scalars().all()

    for team in teams:
        activities.append(
            RecentActivity(
                id=f"team-{team.id}",
                type="team",
                title=f"Created team: {team.name}",
                description=team.description or "No description",
                timestamp=(
                    team.created_at.isoformat()
                    if team.created_at
                    else datetime.utcnow().isoformat()
                ),
            )
        )

    # Sort all activities by timestamp (most recent first)
    activities.sort(key=lambda x: x.timestamp, reverse=True)

    # Return only the requested limit
    return activities[:limit]
