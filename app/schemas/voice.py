from pydantic import BaseModel


class VoiceTokenResponse(BaseModel):
    access_token: str
    config_id: str
