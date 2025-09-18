from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    contact_number = Column(String(11), unique=True, nullable=False)
    address = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)

    onboarding_data = relationship(
        "Onboarding", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    user_problem = relationship(
        "UserProblem", back_populates="user", cascade="all, delete-orphan"
    )
    session_requirement = relationship(
        "SessionRequirement", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )


class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    primary_goal = Column(String, nullable=False)
    pain_score = Column(Integer, nullable=False)
    preferred_schedule = Column(Integer, nullable=False)
    custom_allowed_days = Column(ARRAY(Integer), nullable=True)

    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    user = relationship("User", back_populates="onboarding_data")


class UserProblem(Base):
    __tablename__ = "user_problems"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    problem_area = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(
        Integer, ForeignKey("exercises.id"), nullable=False, index=True
    )
    user = relationship("User", back_populates="user_problem")
    exercise = relationship("Exercise", back_populates="user_problem")
