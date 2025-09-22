from typing import List, Dict, Literal, Union
from pydantic import BaseModel


class PoseSequence(BaseModel):
    list_landmarks: List[List[float]]
    exercise_name: str


class ConfigPayload(BaseModel):
    filename: str
    exercise: str
    category: str


class FramePayload(BaseModel):
    timestamp: str
    landmarks: Dict[str, List[float]]


class WebsocketMessage(BaseModel):
    event: Literal["config", "frame", "end"]
    payload: Union[ConfigPayload, FramePayload, Dict]
