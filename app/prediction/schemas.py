from typing import List, Dict
from pydantic import BaseModel


class PoseSequence(BaseModel):
    list_landmarks: List[List[float]]
    exercise_name: str


class DatasetBase(BaseModel):
    filename: str
    exercise: str
    positions: Dict[str, Dict[str, List[float]]]
    is_incorrect: bool
