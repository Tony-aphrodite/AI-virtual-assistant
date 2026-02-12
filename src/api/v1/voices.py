"""
REST API endpoints for voice profile management.
"""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.db.session import get_db
from src.models.voice_profile import VoiceProfile
from src.schemas.voice import VoiceProfileResponse, VoiceTestRequest, VoiceTestResponse
from src.services.voice.elevenlabs_service import get_elevenlabs_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=list[VoiceProfileResponse])
async def list_voices(
    db: AsyncSession = Depends(get_db),
) -> list[VoiceProfileResponse]:
    """
    List all voice profiles.

    Returns:
        List of voice profiles
    """
    try:
        query = select(VoiceProfile).order_by(VoiceProfile.created_at.desc())
        result = await db.execute(query)
        voices = result.scalars().all()

        return [VoiceProfileResponse.model_validate(v) for v in voices]

    except Exception as e:
        logger.error("Failed to list voices", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list voices")


@router.get("/{voice_id}", response_model=VoiceProfileResponse)
async def get_voice(
    voice_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> VoiceProfileResponse:
    """
    Get details for a specific voice profile.

    Args:
        voice_id: Voice profile UUID
        db: Database session

    Returns:
        Voice profile details
    """
    try:
        query = select(VoiceProfile).where(VoiceProfile.id == voice_id)
        result = await db.execute(query)
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(status_code=404, detail="Voice profile not found")

        return VoiceProfileResponse.model_validate(voice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get voice", error=str(e), voice_id=str(voice_id))
        raise HTTPException(status_code=500, detail="Failed to get voice")


@router.post("/clone", response_model=VoiceProfileResponse)
async def clone_voice(
    name: str = Form(...),
    description: str = Form(None),
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> VoiceProfileResponse:
    """
    Clone a new voice from audio samples.

    Args:
        name: Name for the voice profile
        description: Optional description
        files: Audio files (at least 1 minute total)
        db: Database session

    Returns:
        Created voice profile
    """
    try:
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="At least one audio file is required")

        # Save uploaded files temporarily
        temp_dir = Path("/tmp/voice_samples")
        temp_dir.mkdir(exist_ok=True)

        audio_paths = []
        for file in files:
            if not file.filename:
                continue

            file_path = temp_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            audio_paths.append(file_path)

        if len(audio_paths) == 0:
            raise HTTPException(status_code=400, detail="No valid audio files provided")

        # Clone voice with ElevenLabs
        elevenlabs = get_elevenlabs_service()
        voice_id = await elevenlabs.clone_voice(
            name=name,
            audio_files=audio_paths,
            description=description,
        )

        # Create voice profile in database
        voice_profile = VoiceProfile(
            name=name,
            description=description,
            elevenlabs_voice_id=voice_id,
            sample_audio_urls=[str(p) for p in audio_paths],
            is_active=True,
        )
        db.add(voice_profile)
        await db.commit()
        await db.refresh(voice_profile)

        # Clean up temp files
        for path in audio_paths:
            try:
                path.unlink()
            except Exception:
                pass

        logger.info("Voice cloned successfully", voice_id=voice_id, name=name)

        return VoiceProfileResponse.model_validate(voice_profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to clone voice", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clone voice: {str(e)}")


@router.post("/{voice_id}/test", response_model=VoiceTestResponse)
async def test_voice(
    voice_id: UUID,
    request: VoiceTestRequest,
    db: AsyncSession = Depends(get_db),
) -> VoiceTestResponse:
    """
    Test a voice profile with sample text.

    Args:
        voice_id: Voice profile UUID
        request: Test request with text
        db: Database session

    Returns:
        Audio URL for the test
    """
    try:
        # Get voice profile
        query = select(VoiceProfile).where(VoiceProfile.id == voice_id)
        result = await db.execute(query)
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(status_code=404, detail="Voice profile not found")

        # Generate speech
        elevenlabs = get_elevenlabs_service()
        audio_bytes = await elevenlabs.text_to_speech(
            text=request.text,
            voice_id=voice.elevenlabs_voice_id,
        )

        # Save to temporary location (in production, upload to S3/Cloud Storage)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(audio_bytes)
            audio_url = f.name

        logger.info("Voice test generated", voice_id=str(voice_id))

        return VoiceTestResponse(
            audio_url=f"/tmp/audio/{Path(audio_url).name}",
            duration_seconds=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to test voice", error=str(e), voice_id=str(voice_id))
        raise HTTPException(status_code=500, detail=f"Failed to test voice: {str(e)}")


@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a voice profile.

    Args:
        voice_id: Voice profile UUID
        db: Database session

    Returns:
        Success message
    """
    try:
        # Get voice profile
        query = select(VoiceProfile).where(VoiceProfile.id == voice_id)
        result = await db.execute(query)
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(status_code=404, detail="Voice profile not found")

        # Delete from ElevenLabs
        try:
            elevenlabs = get_elevenlabs_service()
            await elevenlabs.delete_voice(voice.elevenlabs_voice_id)
        except Exception as e:
            logger.warning("Failed to delete voice from ElevenLabs", error=str(e))

        # Delete from database
        await db.delete(voice)
        await db.commit()

        logger.info("Voice deleted", voice_id=str(voice_id))

        return {"status": "deleted", "id": str(voice_id)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete voice", error=str(e), voice_id=str(voice_id))
        raise HTTPException(status_code=500, detail=f"Failed to delete voice: {str(e)}")
