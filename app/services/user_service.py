from sqlalchemy.orm import Session

from app.models.user import User


def get_or_create_user(db: Session, google_user: dict) -> User:
    user = db.query(User).filter(User.google_id == google_user["sub"]).first()

    if user is None:
        user = User(
            google_id=google_user["sub"],
            email=google_user.get("email"),
            name=google_user.get("name"),
            profile_image=google_user.get("picture"),
            auth_provider="google",
        )
        db.add(user)
    else:
        user.email = google_user.get("email")
        user.name = google_user.get("name")
        user.profile_image = google_user.get("picture")

    db.commit()
    db.refresh(user)
    return user
