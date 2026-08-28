import httpx

from app.core.config import settings

_TOKEN_URL = "https://api.hume.ai/oauth2-cc/token"


class HumeAuthError(Exception):
    """Raised when Hume's OAuth endpoint refuses or fails to issue a token."""


async def create_hume_access_token() -> str:
    """Exchanges HUME_API_KEY/HUME_SECRET_KEY for a short-lived access token.

    Server-side only: the API key and secret never leave this function, and
    neither they nor the resulting token are logged. Callers (the /voice/token
    route) hand only the token to the client.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                _TOKEN_URL,
                auth=(settings.hume_api_key, settings.hume_secret_key),
                data={"grant_type": "client_credentials"},
            )
        except httpx.HTTPError as exc:
            raise HumeAuthError("Could not reach Hume's token endpoint") from exc

    if response.status_code != 200:
        raise HumeAuthError(
            f"Hume token endpoint returned status {response.status_code}"
        )

    access_token = response.json().get("access_token")
    if not access_token:
        raise HumeAuthError("Hume token response had no access_token")

    return access_token
