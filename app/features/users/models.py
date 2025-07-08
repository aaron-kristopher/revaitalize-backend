from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from app.db.database import Base


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)


class Onboarding(BaseModel):
    user_id: int
    primary_goal: str
    pain_score: int
    preferred_schedule: int
