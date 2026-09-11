from typing import Literal

from pydantic import BaseModel


class ToolResult(BaseModel):
    """What the Flutter app got back after executing a tool call the agent
    requested on the previous /voice/turn call. `content` is already a
    complete, ready-to-speak sentence (see AgentrixToolRegistry) — spoken
    directly, with no second Gemini call to "reply" to it (see
    agentrix_agent.py for why). `tool_call_id`/`name` aren't read for that,
    but stay on the wire for logging/debugging a mismatched round trip.
    """

    tool_call_id: str
    name: str
    content: str


class VoiceTurnRequest(BaseModel):
    id_token: str

    # Required for a fresh utterance; omitted once `tool_result` is set,
    # since that call doesn't touch Gemini's audio understanding at all.
    audio_base64: str | None = None
    tool_result: ToolResult | None = None


class VoiceTurnResponse(BaseModel):
    type: Literal["tool_call", "reply"]

    # type == "tool_call"
    tool_call_id: str | None = None
    name: str | None = None
    arguments: dict | None = None

    # type == "reply" — text only, spoken on-device (see app/api/voice.py
    # for why this doesn't also carry synthesized audio).
    text: str | None = None
