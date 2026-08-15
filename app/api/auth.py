from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import GoogleLoginRequest
from app.services.google_auth import verify_google_token
from app.services.user_service import get_or_create_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/google")
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):

    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        )

    user = get_or_create_user(db, google_user)

    return {
        "message": "Google authentication successful",
        "id": user.id,
        "google_id": user.google_id,
        "email": user.email,
        "name": user.name,
        "picture": user.profile_image,
    }
