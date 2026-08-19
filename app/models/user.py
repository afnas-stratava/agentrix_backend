from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_image: Mapped[str | None] = mapped_column(String, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String, default="google")
    biological_sex: Mapped[str | None] = mapped_column(String, nullable=True)

    # Onboarding step 2 — "A few numbers about you" (see `body_screen.dart`).
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String, nullable=True)

    # Onboarding step 3 — "What are you working towards?" (see
    # `goals_screen.dart`). `goals`/`conditions` are genuinely list-valued,
    # unlike the other onboarding columns, so JSON here is the field's actual
    # shape — not a stand-in for one column per field.
    goals: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    target_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    conditions: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Onboarding step 4 — "How do you eat?" (see `diet_screen.dart`).
    # `cuisines` keeps tap order — that's the ranking the restaurant ranker
    # weights by — so it's a JSON array, not an unordered set.
    diet_pattern: Mapped[str | None] = mapped_column(String, nullable=True)
    allergies: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    restrictions: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    cuisines: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Set once the user reaches the end of onboarding (`goMain()` in
    # `app_stage_provider.dart`) — read back on a later `/auth/google` so a
    # reinstall or a second device skips straight past onboarding instead of
    # re-asking someone who already answered everything.
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
