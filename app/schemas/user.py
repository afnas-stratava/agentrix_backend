from typing import Literal

from pydantic import BaseModel


class UpdateBiologicalSexRequest(BaseModel):
    id_token: str
    biological_sex: Literal["male", "female", "unspecified"]


class UpdateBodyRequest(BaseModel):
    id_token: str
    height_cm: float | None = None
    weight_kg: float | None = None
    age: int | None = None
    activity_level: Literal["sedentary", "light", "moderate", "active", "very-active"] | None = None


HealthGoalName = Literal["loseWeight", "buildMuscle", "manageCondition", "generalWellness"]

ConditionName = Literal[
    "prediabetes",
    "type2-diabetes",
    "hypertension",
    "high-cholesterol",
    "pcos",
    "hypothyroidism",
    "anaemia",
    "fatty-liver",
]


class UpdateGoalsRequest(BaseModel):
    id_token: str
    goals: list[HealthGoalName] | None = None
    target_weight_kg: float | None = None
    conditions: list[ConditionName] | None = None


DietPatternName = Literal[
    "omnivore", "vegetarian", "lactose-free", "vegan", "pescatarian", "halal"
]

AllergyName = Literal[
    "peanut", "tree-nut", "dairy", "gluten", "soy", "egg", "shellfish", "fish", "sesame"
]

RestrictionName = Literal[
    "low-sodium", "low-carb", "no-added-sugar", "low-fodmap", "no-alcohol", "no-fried"
]

CuisineName = Literal[
    "american", "mexican", "mediterranean", "indian", "chinese", "korean", "vegetarian"
]


class UpdateDietRequest(BaseModel):
    id_token: str
    diet_pattern: DietPatternName | None = None
    allergies: list[AllergyName] | None = None
    restrictions: list[RestrictionName] | None = None
    cuisines: list[CuisineName] | None = None


class MarkOnboardingCompleteRequest(BaseModel):
    id_token: str
