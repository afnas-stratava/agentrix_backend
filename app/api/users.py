from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import (
    MarkOnboardingCompleteRequest,
    UpdateBiologicalSexRequest,
    UpdateBodyRequest,
    UpdateDietRequest,
    UpdateGoalsRequest,
)
from app.services.google_auth import verify_google_token
from app.services.user_service import (
    mark_onboarding_complete,
    set_biological_sex,
    set_body,
    set_diet,
    set_goals,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.patch("/me/sex")
def update_biological_sex(request: UpdateBiologicalSexRequest, db: Session = Depends(get_db)):

    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        )

    user = set_biological_sex(db, google_user["sub"], request.biological_sex)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found — sign in with /auth/google first",
        )

    return {
        "id": user.id,
        "biological_sex": user.biological_sex,
    }


@router.patch("/me/body")
def update_body(request: UpdateBodyRequest, db: Session = Depends(get_db)):

    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        )

    user = set_body(
        db,
        google_user["sub"],
        request.height_cm,
        request.weight_kg,
        request.age,
        request.activity_level,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found — sign in with /auth/google first",
        )

    return {
        "id": user.id,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "age": user.age,
        "activity_level": user.activity_level,
    }


@router.patch("/me/goals")
def update_goals(request: UpdateGoalsRequest, db: Session = Depends(get_db)):

    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        )

    user = set_goals(
        db,
        google_user["sub"],
        request.goals,
        request.target_weight_kg,
        request.conditions,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found — sign in with /auth/google first",
        )

    return {
        "id": user.id,
        "goals": user.goals,
        "target_weight_kg": user.target_weight_kg,
        "conditions": user.conditions,
    }


@router.patch("/me/diet")
def update_diet(request: UpdateDietRequest, db: Session = Depends(get_db)):

    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        )

    user = set_diet(
        db,
        google_user["sub"],
        request.diet_pattern,
        request.allergies,
        request.restrictions,
        request.cuisines,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found — sign in with /auth/google first",
        )

    return {
        "id": user.id,
        "diet_pattern": user.diet_pattern,
        "allergies": user.allergies,
        "restrictions": user.restrictions,
        "cuisines": user.cuisines,
    }


@router.patch("/me/onboarding-complete")
def onboarding_complete(request: MarkOnboardingCompleteRequest, db: Session = Depends(get_db)):

    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        )

    user = mark_onboarding_complete(db, google_user["sub"])

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found — sign in with /auth/google first",
        )

    return {
        "id": user.id,
        "onboarding_complete": user.onboarding_complete,
    }
