from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.voice import VoiceTokenResponse
from app.services.hume_auth import HumeAuthError, create_hume_access_token

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


@router.get("/token", response_model=VoiceTokenResponse)
async def get_voice_token():
    """Issues a short-lived Hume EVI access token for the Flutter app.

    The Hume API key and secret stay server-side; only the token and the
    (non-secret) config_id are returned. Flutter opens the EVI WebSocket
    directly with these — the backend is not in the audio path.
    """
    try:
        access_token = await create_hume_access_token()
    except HumeAuthError:
        raise HTTPException(
            status_code=500,
            detail="Could not create a Hume voice session. Try again shortly.",
        )

    return VoiceTokenResponse(access_token=access_token, config_id=settings.hume_config_id)
