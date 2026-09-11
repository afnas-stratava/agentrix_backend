import logging

from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level and reused across every call, not created fresh per request:
# `Request` wraps a `requests.Session`, and Google's signing certs are only
# cached against *that* session's lifetime. A new `Request()` per call meant
# a fresh session every time — no cert caching across requests at all, so
# every single token verification paid for a live HTTP round trip to
# Google's cert endpoint on top of the actual signature check.
_google_auth_request = requests.Request()


def verify_google_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            _google_auth_request,
            settings.google_server_client_id,
        )

        return idinfo

    except ValueError as exc:
        logger.warning("Google ID token verification failed: %s", exc)
        raise ValueError("Invalid Google ID token") from exc
