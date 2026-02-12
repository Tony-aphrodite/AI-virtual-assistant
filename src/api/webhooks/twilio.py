"""
Twilio webhook endpoints for handling phone calls.
"""

from fastapi import APIRouter, Depends, Form, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.core.security import validate_twilio_signature
from src.db.session import get_db
from src.services.phone.call_handler import get_call_handler

logger = get_logger(__name__)

router = APIRouter()


@router.post("/voice")
async def handle_incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Handle incoming voice call from Twilio.

    This webhook is called when a call is received.
    Returns TwiML to control the call flow.
    """
    try:
        logger.info(
            "Incoming call webhook",
            call_sid=CallSid,
            from_number=From,
            to_number=To,
            status=CallStatus,
        )

        # Validate Twilio signature (optional but recommended)
        # In production, uncomment this:
        # signature = request.headers.get("X-Twilio-Signature", "")
        # url = str(request.url)
        # form_data = await request.form()
        # params = dict(form_data)
        #
        # if not validate_twilio_signature(url, params, signature):
        #     logger.warning("Invalid Twilio signature", call_sid=CallSid)
        #     return Response(content="Unauthorized", status_code=401)

        # Handle the call
        call_handler = get_call_handler()
        twiml = await call_handler.handle_incoming_call(
            call_sid=CallSid,
            from_number=From,
            to_number=To,
            db=db,
        )

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error("Error handling incoming call", error=str(e), call_sid=CallSid)
        # Return error TwiML
        error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-ES">Lo siento, hay un problema técnico. Por favor, intenta más tarde.</Say>
    <Hangup/>
</Response>"""
        return Response(content=error_twiml, media_type="application/xml")


@router.post("/gather")
async def handle_speech_input(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(None),
    Confidence: str = Form(None),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Handle speech input gathered from the caller.

    This webhook is called after the user speaks.
    Returns TwiML with AI response.
    """
    try:
        logger.info(
            "Speech input gathered",
            call_sid=CallSid,
            speech_preview=SpeechResult[:100] if SpeechResult else None,
            confidence=Confidence,
        )

        if not SpeechResult:
            # No speech detected
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-ES">No te escuché. ¿Puedes repetir por favor?</Say>
    <Gather input="speech" action="/webhooks/twilio/gather" method="POST" speechTimeout="auto" language="es-ES"/>
    <Hangup/>
</Response>"""
            return Response(content=twiml, media_type="application/xml")

        # Process speech and generate response
        call_handler = get_call_handler()
        twiml = await call_handler.handle_user_speech(
            call_sid=CallSid,
            speech_result=SpeechResult,
            db=db,
        )

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error("Error handling speech input", error=str(e), call_sid=CallSid)
        error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-ES">Disculpa, tuve un problema. ¿Puedes repetir?</Say>
    <Gather input="speech" action="/webhooks/twilio/gather" method="POST" speechTimeout="auto" language="es-ES"/>
    <Hangup/>
</Response>"""
        return Response(content=error_twiml, media_type="application/xml")


@router.post("/status")
async def handle_call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    CallDuration: str = Form(None),
    RecordingUrl: str = Form(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Handle call status updates from Twilio.

    This webhook is called when call status changes.
    """
    try:
        logger.info(
            "Call status update",
            call_sid=CallSid,
            status=CallStatus,
            duration=CallDuration,
        )

        # If call completed, update records
        if CallStatus == "completed":
            call_handler = get_call_handler()
            await call_handler.handle_call_completed(
                call_sid=CallSid,
                duration=int(CallDuration) if CallDuration else None,
                recording_url=RecordingUrl,
                db=db,
            )

        return {"status": "received"}

    except Exception as e:
        logger.error("Error handling call status", error=str(e), call_sid=CallSid)
        return {"status": "error", "message": str(e)}


@router.post("/recording")
async def handle_recording_callback(
    CallSid: str = Form(...),
    RecordingSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingStatus: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Handle recording completion callback.

    This webhook is called when a recording is ready.
    """
    try:
        logger.info(
            "Recording callback",
            call_sid=CallSid,
            recording_sid=RecordingSid,
            status=RecordingStatus,
        )

        # Update call record with recording URL
        from sqlalchemy import select, update
        from src.models.call import Call

        await db.execute(
            update(Call)
            .where(Call.twilio_call_sid == CallSid)
            .values(recording_url=RecordingUrl)
        )
        await db.commit()

        return {"status": "received"}

    except Exception as e:
        logger.error("Error handling recording", error=str(e), call_sid=CallSid)
        return {"status": "error", "message": str(e)}
