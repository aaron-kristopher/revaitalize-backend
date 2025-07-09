from typing import List
from pydantic import BaseModel


class PoseSequence(BaseModel):
    list_landmarks: List[List[float]]
    exercise_name: str
