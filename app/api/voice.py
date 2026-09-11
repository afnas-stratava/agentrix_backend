import logging
import time

from fastapi import APIRouter, HTTPException

from app.schemas.voice import VoiceTurnRequest, VoiceTurnResponse
from app.services.agentrix_agent import run_agent_turn
from app.services.google_auth import verify_google_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


@router.post("/turn", response_model=VoiceTurnResponse)
async def voice_turn(request: VoiceTurnRequest):
    """One turn of the voice assistant: the app records a clip, sends it
    here, and gets back either a tool to run or a spoken reply.

    A tool call is finished on this same endpoint without going back to
    Gemini at all: the tool's own return string is already a complete,
    ready-to-speak sentence (see AgentrixToolRegistry), so `tool_result`
    goes straight back as the reply — a full LLM round trip (and the audio
    re-upload that would go with it) saved on every tool-based question.

    Replies are text only — the app speaks them with on-device TTS rather
    than Gemini's own, which measured at 5-7s per reply with no faster
    same-quality alternative available. That's a real trade of voice
    quality for responsiveness, made deliberately, not an oversight.

    Requires the same Google ID token issued at sign-in as every other
    per-user endpoint (see users.py) — this call spends a real Gemini API
    call, so it isn't left open to anyone who finds the URL.
    """
    turn_started = time.monotonic()

    t0 = time.monotonic()
    try:
        verify_google_token(request.id_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")
    logger.info("voice_turn: token verify took %.2fs", time.monotonic() - t0)

    if request.tool_result is not None:
        text = request.tool_result.content
        logger.info("voice_turn: total (tool result -> reply) %.2fs", time.monotonic() - turn_started)
        return VoiceTurnResponse(type="reply", text=text)

    if not request.audio_base64:
        raise HTTPException(
            status_code=400,
            detail="audio_base64 is required for a new question.",
        )

    t0 = time.monotonic()
    try:
        result = await run_agent_turn(request.audio_base64)
    except Exception:
        logger.exception("run_agent_turn failed")
        raise HTTPException(
            status_code=500,
            detail="Could not process that. Try again shortly.",
        )
    logger.info(
        "voice_turn: Gemini understanding+decision took %.2fs (audio %d bytes)",
        time.monotonic() - t0,
        len(request.audio_base64),
    )
    logger.info("voice_turn: total %.2fs", time.monotonic() - turn_started)

    if result.is_tool_call:
        return VoiceTurnResponse(
            type="tool_call",
            tool_call_id=result.tool_call_id,
            name=result.tool_name,
            arguments=result.tool_arguments,
        )

    return VoiceTurnResponse(type="reply", text=result.text)
