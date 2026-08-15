import logging

from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_google_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_server_client_id,
        )

        return idinfo

    except ValueError as exc:
        logger.warning("Google ID token verification failed: %s", exc)
        raise ValueError("Invalid Google ID token") from exc
