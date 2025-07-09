from pydantic import BaseModel
from typing import Optional


class ExerciseBase(BaseModel):
    name: str


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str]


class ExerciseOut(ExerciseBase):
    id: int
    name: str

    class Config:
        from_attributes = True
