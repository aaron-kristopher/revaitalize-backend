from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Float

from datetime import datetime
from zoneinfo import ZoneInfo

from app.db.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    datetime_start = Column(
        DateTime, default=datetime.now(ZoneInfo("Asia/Manila")), nullable=False
    )
    datetime_end = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, nullable=True)
    session_quality_score = Column(Float, nullable=True)
    error_flag = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(
        Integer, ForeignKey("exercises.id"), nullable=False, index=True
    )

    user = relationship("User", back_populates="sessions")
    exercise = relationship("Exercise", back_populates="session")
    exercise_sets = relationship(
        "ExerciseSet", back_populates="session", cascade="all, delete-orphan"
    )


class SessionRequirement(Base):
    __tablename__ = "session_requirements"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    number_of_reps = Column(Integer, nullable=False)
    number_of_sets = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(
        Integer, ForeignKey("exercises.id"), nullable=False, index=True
    )

    user = relationship("User", back_populates="session_requirement")
    exercise = relationship("Exercise", back_populates="session_requirement")


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    set_number = Column(Integer, nullable=False)
    set_quality_score = Column(Float, nullable=True)
    is_completed = Column(Boolean, nullable=True)
    error_flag = Column(String, nullable=True)

    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)

    session = relationship("Session", back_populates="exercise_sets")
    repetitions = relationship(
        "Repetition", back_populates="exercise_set", cascade="all, delete-orphan"
    )


class Repetition(Base):
    __tablename__ = "repetitions"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    rep_number = Column(Integer, nullable=False)
    rep_quality_score = Column(Float, nullable=True)
    is_completed = Column(Boolean, nullable=True)
    error_flag = Column(String, nullable=True)

    set_id = Column(Integer, ForeignKey("exercise_sets.id"), nullable=False, index=True)

    exercise_set = relationship("ExerciseSet", back_populates="repetitions")
