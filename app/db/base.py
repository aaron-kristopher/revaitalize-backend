from pydantic_settings import BaseSettings
from pydantic import Field

from app.db.database import Base

from app.features.users.models import User, Onboarding, UserProblem
from app.features.sessions.models import (
    Session,
    SessionRequirement,
    ExerciseSet,
    Repetition,
)
from app.features.exercises.models import Exercise

_ = [
    User,
    Onboarding,
    UserProblem,
    Session,
    SessionRequirement,
    ExerciseSet,
    Repetition,
    Exercise,
    Base,
]


class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")

    class Config:
        env_file = ".env"
        extra = "allow"
