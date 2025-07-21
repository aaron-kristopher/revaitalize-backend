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
