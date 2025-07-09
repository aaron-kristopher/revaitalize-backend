from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base  # Make sure your Base is importable


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)

    onboarding_data = relationship("Onboarding", back_populates="user", uselist=False)
    problems = relationship("UserProblem", back_populates="user")


class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, index=True)
    primary_goal = Column(String, nullable=False)
    pain_score = Column(Integer, nullable=False)
    preferred_schedule = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="onboarding_data")


class UserProblem(Base):
    __tablename__ = "user_problems"

    id = Column(Integer, primary_key=True, index=True)
    problem_area = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    user = relationship("User", back_populates="problems")
    exercise = relationship("Exercise", back_populates="problems")
