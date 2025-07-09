from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from . import crud, schemas

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.post(
    "/", response_model=schemas.ExerciseOut, status_code=status.HTTP_201_CREATED
)
def create_new_exercise(
    exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)
):
    """
    Create a new exercise.
    """
    db_exercise = crud.get_exercise_by_name(db, name=exercise.name)
    if db_exercise:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An exercise with this name already exists.",
        )
    return crud.create_exercise(db=db, exercise=exercise)


@router.get("/all", response_model=List[schemas.ExerciseOut])
def get_all_exercises_route(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve a list of all exercises.
    """
    exercises = crud.get_all_exercises(db=db, skip=skip, limit=limit)
    return exercises


@router.get("/{exercise_id}", response_model=schemas.ExerciseOut)
def get_exercise_by_id_route(exercise_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single exercise by its ID.
    """
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with ID {exercise_id} not found.",
        )
    return db_exercise


@router.put("/{exercise_id}", response_model=schemas.ExerciseOut)
def update_exercise_route(
    exercise_id: int,
    exercise_update: schemas.ExerciseUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing exercise's details.
    """
    updated_exercise = crud.update_exercise(
        db, exercise_id=exercise_id, exercise_update=exercise_update
    )
    if updated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with ID {exercise_id} not found.",
        )

    return updated_exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_route(exercise_id: int, db: Session = Depends(get_db)):
    """
    Delete an exercise.
    """
    deleted_exercise = crud.delete_exercise(db, exercise_id=exercise_id)
    if deleted_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with ID {exercise_id} not found.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
