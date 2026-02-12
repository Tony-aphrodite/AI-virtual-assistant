"""
Dashboard API endpoints for statistics and recent activity.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.db.session import get_db
from src.models.call import Call, CallStatus
from src.schemas.call import CallResponse

logger = get_logger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get dashboard statistics.

    Returns:
        Statistics including call counts, averages, etc.
    """
    try:
        # Total calls
        total_query = select(func.count()).select_from(Call)
        total_result = await db.execute(total_query)
        total_calls = total_result.scalar() or 0

        # Today's calls
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_query = select(func.count()).select_from(Call).where(
            Call.created_at >= today_start
        )
        today_result = await db.execute(today_query)
        today_calls = today_result.scalar() or 0

        # Active calls (in-progress)
        active_query = select(func.count()).select_from(Call).where(
            Call.status == CallStatus.IN_PROGRESS
        )
        active_result = await db.execute(active_query)
        active_calls = active_result.scalar() or 0

        # Average duration (completed calls only)
        avg_duration_query = select(func.avg(Call.duration)).where(
            Call.status == CallStatus.COMPLETED,
            Call.duration.isnot(None),
        )
        avg_result = await db.execute(avg_duration_query)
        avg_duration = avg_result.scalar() or 0

        # Success rate (completed / total non-active)
        completed_query = select(func.count()).select_from(Call).where(
            Call.status == CallStatus.COMPLETED
        )
        completed_result = await db.execute(completed_query)
        completed_calls = completed_result.scalar() or 0

        success_rate = (
            completed_calls / total_calls if total_calls > 0 else 0
        )

        return {
            "total_calls": total_calls,
            "today_calls": today_calls,
            "active_calls": active_calls,
            "avg_duration": float(avg_duration) if avg_duration else 0,
            "success_rate": success_rate,
        }

    except Exception as e:
        logger.error("Failed to get dashboard stats", error=str(e))
        # Return zeros on error instead of failing
        return {
            "total_calls": 0,
            "today_calls": 0,
            "active_calls": 0,
            "avg_duration": 0,
            "success_rate": 0,
        }


@router.get("/recent", response_model=list[CallResponse])
async def get_recent_calls(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[CallResponse]:
    """
    Get recent calls.

    Args:
        limit: Number of calls to return (max 50)
        db: Database session

    Returns:
        List of recent calls
    """
    try:
        query = (
            select(Call)
            .order_by(desc(Call.created_at))
            .limit(limit)
        )
        result = await db.execute(query)
        calls = result.scalars().all()

        return [CallResponse.model_validate(call) for call in calls]

    except Exception as e:
        logger.error("Failed to get recent calls", error=str(e))
        return []
