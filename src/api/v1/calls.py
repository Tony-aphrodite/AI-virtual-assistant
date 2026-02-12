"""
REST API endpoints for call management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.db.session import get_db
from src.models.call import Call
from src.models.conversation import Conversation
from src.schemas.call import CallListResponse, CallResponse, OutboundCallRequest
from src.schemas.conversation import ConversationResponse
from src.services.phone.twilio_service import get_twilio_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=CallListResponse)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CallListResponse:
    """
    List all calls with pagination.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page
        db: Database session

    Returns:
        Paginated list of calls
    """
    try:
        # Get total count
        count_query = select(func.count()).select_from(Call)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated calls
        offset = (page - 1) * page_size
        query = (
            select(Call)
            .order_by(desc(Call.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        calls = result.scalars().all()

        return CallListResponse(
            items=[CallResponse.model_validate(call) for call in calls],
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error("Failed to list calls", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list calls")


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CallResponse:
    """
    Get details for a specific call.

    Args:
        call_id: Call UUID
        db: Database session

    Returns:
        Call details
    """
    try:
        query = select(Call).where(Call.id == call_id)
        result = await db.execute(query)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(status_code=404, detail="Call not found")

        return CallResponse.model_validate(call)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get call", error=str(e), call_id=str(call_id))
        raise HTTPException(status_code=500, detail="Failed to get call")


@router.get("/{call_id}/conversation", response_model=ConversationResponse)
async def get_call_conversation(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """
    Get conversation for a specific call.

    Args:
        call_id: Call UUID
        db: Database session

    Returns:
        Conversation details
    """
    try:
        query = select(Conversation).where(Conversation.call_id == call_id)
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return ConversationResponse.model_validate(conversation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversation", error=str(e), call_id=str(call_id))
        raise HTTPException(status_code=500, detail="Failed to get conversation")


@router.post("/outbound")
async def make_outbound_call(
    request: OutboundCallRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Initiate an outbound call.

    Args:
        request: Outbound call request
        db: Database session

    Returns:
        Call SID and status
    """
    try:
        twilio = get_twilio_service()

        # Make the call
        call_sid = twilio.make_outbound_call(
            to_number=request.to_number,
            from_number=request.from_number,
        )

        # Create call record
        call = Call(
            twilio_call_sid=call_sid,
            direction="outbound",
            from_number=request.from_number or twilio.phone_number,
            to_number=request.to_number,
            status="initiated",
        )
        db.add(call)
        await db.commit()

        logger.info("Outbound call initiated", call_sid=call_sid, to_number=request.to_number)

        return {
            "call_sid": call_sid,
            "call_id": str(call.id),
            "status": "initiated",
        }

    except Exception as e:
        logger.error("Failed to make outbound call", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to make call: {str(e)}")
