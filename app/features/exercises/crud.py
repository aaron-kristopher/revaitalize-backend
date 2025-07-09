from sqlalchemy.orm import Session
from . import models, schemas

# --- READ ---


def get_exercise(db: Session, exercise_id: int):
    """
    Fetches a single exercise by its primary key ID.
    Returns the SQLAlchemy model instance or None if not found.
    """
    return db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()


def get_exercise_by_name(db: Session, name: str):
    """
    Fetches a single exercise by its unique name.
    Returns the SQLAlchemy model instance or None if not found.
    """
    return db.query(models.Exercise).filter(models.Exercise.name == name).first()


def get_all_exercises(db: Session, skip: int = 0, limit: int = 100):
    """
    Fetches a list of all exercises with pagination.
    """
    return db.query(models.Exercise).offset(skip).limit(limit).all()


# --- CREATE ---


def create_exercise(db: Session, exercise: schemas.ExerciseCreate):
    """
    Creates a new exercise record in the database.
    """
    db_exercise = models.Exercise(name=exercise.name)

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return db_exercise


# --- UPDATE ---


def update_exercise(
    db: Session, exercise_id: int, exercise_update: schemas.ExerciseUpdate
):
    """
    Updates an existing exercise in the database.
    """
    db_exercise = get_exercise(db, exercise_id=exercise_id)

    if not db_exercise:
        return None

    update_data = exercise_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_exercise, key, value)

    db.commit()
    db.refresh(db_exercise)

    return db_exercise


# --- DELETE ---


def delete_exercise(db: Session, exercise_id: int):
    """
    Deletes an exercise from the database.
    """
    db_exercise = get_exercise(db, exercise_id=exercise_id)

    if not db_exercise:
        return None

    db.delete(db_exercise)
    db.commit()

    return db_exercise
