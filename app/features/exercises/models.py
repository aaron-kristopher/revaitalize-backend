from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    user_problem = relationship(
        "UserProblem", back_populates="exercise", cascade="all, delete-orphan"
    )
    session_requirement = relationship(
        "SessionRequirement", back_populates="exercise", cascade="all, delete-orphan"
    )
    session = relationship(
        "Session", back_populates="exercise", cascade="all, delete-orphan"
    )
