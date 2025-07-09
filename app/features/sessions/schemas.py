import datetime
from typing import Optional, List
from pydantic import BaseModel

# ==================================
#    SESSION REQUIREMENT Schemas
# ==================================


class SessionRequirementBase(BaseModel):
    number_of_reps: int
    number_of_sets: int


class SessionRequirementCreate(SessionRequirementBase):
    exercise_id: int
    user_id: int


class SessionRequirementOut(SessionRequirementBase):
    id: int
    user_id: int
    exercise_id: int

    class Config:
        from_attributes = True


class SessionRequirementUpdate(BaseModel):
    number_of_reps: Optional[int]
    number_of_sets: Optional[int]


# ==================================
#        REPETITION Schemas
# ==================================


class RepetitionBase(BaseModel):
    rep_number: int
    rep_quality_score: Optional[float]
    error_flag: Optional[str]


class RepetitionCreate(RepetitionBase):
    pass


class RepetitionOut(RepetitionBase):
    id: int
    set_id: int
    is_completed: bool = True  # A rep is complete once logged

    class Config:
        from_attributes = True


# ==================================
#        EXERCISE SET Schemas
# ==================================


class ExerciseSetBase(BaseModel):
    set_number: int


# Schema for CREATING a Set.
class ExerciseSetCreate(ExerciseSetBase):
    pass


class ExerciseSetOut(ExerciseSetBase):
    id: int
    session_id: int
    set_quality_score: Optional[float] = None
    is_completed: Optional[bool] = None
    error_flag: Optional[str] = None

    class Config:
        from_attributes = True


class ExerciseSetUpdate(BaseModel):
    set_quality_score: Optional[float]
    is_completed: Optional[bool]
    error_flag: Optional[str]


# ==================================
#           SESSION Schemas
# ==================================


class SessionCreate(BaseModel):
    user_id: int
    exercise_id: int


class SessionUpdate(BaseModel):
    is_completed: Optional[bool] = None
    session_quality_score: Optional[float] = None
    error_flag: Optional[str] = None


class SessionOut(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    datetime_start: datetime.datetime
    datetime_end: Optional[datetime.datetime] = None
    is_completed: Optional[bool] = None
    session_quality_score: Optional[float] = None
    error_flag: Optional[str] = None
    sets: List[ExerciseSetOut] = (
        []
    )  # Nests the set data, which in turn nests the repetition data

    class Config:
        from_attributes = True
