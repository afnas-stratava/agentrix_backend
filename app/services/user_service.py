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


def set_biological_sex(db: Session, google_id: str, biological_sex: str) -> User | None:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        return None

    user.biological_sex = biological_sex
    db.commit()
    db.refresh(user)
    return user


def set_body(
    db: Session,
    google_id: str,
    height_cm: float | None,
    weight_kg: float | None,
    age: int | None,
    activity_level: str | None,
) -> User | None:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        return None

    if height_cm is not None:
        user.height_cm = height_cm
    if weight_kg is not None:
        user.weight_kg = weight_kg
    if age is not None:
        user.age = age
    if activity_level is not None:
        user.activity_level = activity_level

    db.commit()
    db.refresh(user)
    return user


def set_goals(
    db: Session,
    google_id: str,
    goals: list[str] | None,
    target_weight_kg: float | None,
    conditions: list[str] | None,
) -> User | None:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        return None

    if goals is not None:
        user.goals = goals
    if target_weight_kg is not None:
        user.target_weight_kg = target_weight_kg
    if conditions is not None:
        user.conditions = conditions

    db.commit()
    db.refresh(user)
    return user


def set_diet(
    db: Session,
    google_id: str,
    diet_pattern: str | None,
    allergies: list[str] | None,
    restrictions: list[str] | None,
    cuisines: list[str] | None,
) -> User | None:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        return None

    if diet_pattern is not None:
        user.diet_pattern = diet_pattern
    if allergies is not None:
        user.allergies = allergies
    if restrictions is not None:
        user.restrictions = restrictions
    if cuisines is not None:
        user.cuisines = cuisines

    db.commit()
    db.refresh(user)
    return user


def mark_onboarding_complete(db: Session, google_id: str) -> User | None:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        return None

    user.onboarding_complete = True
    db.commit()
    db.refresh(user)
    return user
