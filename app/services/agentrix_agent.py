"""The LangChain agent behind the voice assistant.

Gemini handles everything now: it understands the user's spoken audio
directly (no separate transcription step), decides whether to reply or
call a tool, and (via gemini_tts.py) speaks the reply back. See
app/api/voice.py for the HTTP contract this is wired into.

Each call to run_agent_turn is independent, stateless context — there is no
growing multi-turn conversation history. That's a deliberate simplification
for a "tap mic, ask one thing, get one answer" interaction, not an
oversight: threading real cross-turn memory through would mean either the
backend holding session state (infrastructure this single-user mobile app
doesn't otherwise need) or the client resending every prior audio clip
(payload that only grows). Add one of those if the assistant needs to
handle follow-ups like "and yesterday?" later.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

_MODEL_NAME = "gemini-flash-latest"

_SYSTEM_PROMPT = """\
You are Agentrix, a concise, warm voice assistant inside a personal health \
app. Keep replies to 1-3 short sentences — they are spoken aloud, not read.

You are not a clinician. Never diagnose a condition or interpret what a \
result "means" medically; if something sounds concerning, say so plainly \
and suggest they see a clinician.

You can navigate the app or read the user's live health metrics using the \
tools available to you — call the matching tool whenever the user asks to \
go somewhere in the app or asks about a specific metric. Only state facts \
a tool actually returned; never invent a number.

Stay strictly on health, wellness, and using this app. If asked about \
anything else, decline briefly and steer back.\
"""

# Mirrors AgentrixToolRegistry in the Flutter app (lib/presentation/voice/
# agentrix_tool_registry.dart) — both must agree on names for a tool call to
# reach the client and be understood. Declared here as schemas only: this
# backend never executes one, it just decides *whether* to call it. The
# app executes it and speaks the tool's own return string directly (see
# app/api/voice.py) — every tool already returns a complete, ready-to-speak
# sentence, so there's no second Gemini call needed to "reply" to a tool
# result; that would just be re-asking the model to say something it's
# already been told verbatim, at the cost of a full extra round trip (plus
# whatever audio would need to go with it) on every tool-based question.
_TOOL_DESCRIPTIONS: dict[str, str] = {
    "open_dashboard": "Open the Today/dashboard tab when the user asks to go home or see their overview.",
    "open_food_diary": "Open the food diary when the user asks to log a meal or see what they've eaten.",
    "open_insights": "Open the Insights tab when the user asks about trends or correlations in their data.",
    "open_labs": "Open the Labs tab when the user asks about blood work or lab results.",
    "open_settings": "Open Settings when the user asks to change a setting or their profile.",
    "open_sleep": "Open sleep detail when the user asks about their sleep.",
    "get_daily_steps": "Answer when the user asks how many steps they've taken today.",
    "get_heart_rate_variability": "Answer when the user asks about their HRV.",
    "get_resting_heart_rate": "Answer when the user asks about their resting heart rate.",
    "get_sleep": "Answer when the user asks how long or how well they slept.",
    "get_active_energy": "Answer when the user asks how many calories they've burned.",
}

_TOOLS = [
    {
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": {}},
    }
    for name, description in _TOOL_DESCRIPTIONS.items()
]


def _build_model():
    return ChatGoogleGenerativeAI(
        model=_MODEL_NAME,
        google_api_key=settings.gemini_api_key,
        temperature=0.4,
    ).bind_tools(_TOOLS)


def _text_of(content) -> str:
    """`AIMessage.content` is a plain string for a simple reply, but can come
    back as a list of content-part dicts (`{"type": "text", "text": ...,
    "extras": {...}}`) whenever Gemini attaches extra metadata to the
    response — seen in testing. Handles both."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part if isinstance(part, str) else part.get("text", "")
            for part in content
            if isinstance(part, str) or part.get("type") == "text"
        )
    return ""


class AgentTurnResult:
    """Either a spoken reply, or a tool the client should execute."""

    def __init__(
        self,
        *,
        text: str | None,
        tool_name: str | None,
        tool_call_id: str | None,
        tool_arguments: dict | None,
    ):
        self.text = text
        self.tool_name = tool_name
        self.tool_call_id = tool_call_id
        self.tool_arguments = tool_arguments

    @property
    def is_tool_call(self) -> bool:
        return self.tool_name is not None


async def run_agent_turn(audio_base64: str) -> AgentTurnResult:
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=[{"type": "media", "mime_type": "audio/wav", "data": audio_base64}]),
    ]
    model = _build_model()
    result: AIMessage = await model.ainvoke(messages)

    if result.tool_calls:
        call = result.tool_calls[0]
        return AgentTurnResult(
            text=None,
            tool_name=call["name"],
            tool_call_id=call["id"],
            tool_arguments=call["args"],
        )

    return AgentTurnResult(
        text=_text_of(result.content) or "Sorry, could you say that again?",
        tool_name=None,
        tool_call_id=None,
        tool_arguments=None,
    )
