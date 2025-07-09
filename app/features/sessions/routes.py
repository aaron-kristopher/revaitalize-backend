from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from . import (
    crud,
    schemas,
)  # Assumes crud.py and schemas.py are in this 'sessions' folder
from app.features.users import crud as users_crud  # To verify users exist
from app.features.exercises import crud as exercises_crud  # To verify exercises exist

router = APIRouter(tags=["Session"])

# ==================================
#    SESSION REQUIREMENT Routes
# ==================================


@router.post(
    "/users/{user_id}/requirements",
    response_model=schemas.SessionRequirementOut,
    status_code=status.HTTP_201_CREATED,
)
def create_session_requirement_for_user(
    user_id: int,
    requirement: schemas.SessionRequirementCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new session requirement (reps/sets) for a specific user and exercise.
    """
    db_user = users_crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_exercise = exercises_crud.get_exercise(db, exercise_id=requirement.exercise_id)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )

    return crud.create_session_requirement(
        db=db, requirement=requirement, user_id=user_id
    )


@router.get(
    "/users/{user_id}/requirements", response_model=List[schemas.SessionRequirementOut]
)
def get_all_requirements_for_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get all session requirements for a specific user.
    """
    db_user = users_crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.get_user_session_requirements(db=db, user_id=user_id)


@router.put(
    "/requirements/{requirement_id}", response_model=schemas.SessionRequirementOut
)
def update_user_session_requirement(
    requirement_id: int,
    requirement_update: schemas.SessionRequirementUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the reps or sets for a specific session requirement.
    """
    updated_req = crud.update_session_requirement(
        db, requirement_id=requirement_id, requirement_update=requirement_update
    )
    if updated_req is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session requirement not found",
        )
    return updated_req


# ==================================
#           SESSION Routes
# ==================================


@router.post(
    "/sessions/start",
    response_model=schemas.SessionOut,
    status_code=status.HTTP_201_CREATED,
)
def start_new_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    """
    Starts a new exercise session for a user. The request body must contain
    the user_id and the exercise_id.
    """
    db_user = users_crud.get_user(db, user_id=session.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User specified for session not found",
        )

    db_exercise = exercises_crud.get_exercise(db, exercise_id=session.exercise_id)
    if not db_exercise:
        raise HTTPException(
            status_code=404, detail="Exercise specified for session not found"
        )

    return crud.create_session(
        db=db, user_id=session.user_id, exercise_id=session.exercise_id
    )


@router.put("/sessions/{session_id}/end", response_model=schemas.SessionOut)
def end_exercise_session(
    session_id: int,
    session_update: schemas.SessionUpdate,
    db: Session = Depends(get_db),
):
    """
    Marks a session as complete and updates its final scores.
    The request body can contain the final quality score, error flags, etc.
    """
    ended_session = crud.update_session(
        db, session_id=session_id, session_update=session_update
    )
    if not ended_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return ended_session


@router.get("/sessions/{session_id}", response_model=schemas.SessionOut)
def get_session_details(session_id: int, db: Session = Depends(get_db)):
    """

    Gets all details for a specific session, including its nested sets and repetitions.
    """
    db_session = crud.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


# ==================================
#       EXERCISE SET Routes
# ==================================


@router.post(
    "/sessions/{session_id}/sets",
    response_model=schemas.ExerciseSetOut,
    status_code=status.HTTP_201_CREATED,
)
def add_set_to_session(
    session_id: int, set_data: schemas.ExerciseSetCreate, db: Session = Depends(get_db)
):
    """
    Creates a new set record and associates it with a session.
    """
    # Verify the parent session exists
    db_session = crud.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found to add set to")

    return crud.create_exercise_set(db=db, set_create=set_data, session_id=session_id)


@router.put("/sets/{set_id}", response_model=schemas.ExerciseSetOut)
def update_exercise_set_details(
    set_id: int, set_update: schemas.ExerciseSetUpdate, db: Session = Depends(get_db)
):
    """
    Updates the details of a specific set (e.g., quality score) after it's completed.
    """
    updated_set = crud.update_exercise_set(db, set_id=set_id, set_update=set_update)
    if updated_set is None:
        raise HTTPException(status_code=404, detail="Set not found")
    return updated_set


# ==================================
#         REPETITION Routes
# ==================================


@router.post(
    "/sets/{set_id}/repetitions",
    response_model=schemas.RepetitionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_repetition_to_set(
    set_id: int, rep_data: schemas.RepetitionCreate, db: Session = Depends(get_db)
):
    """
    Logs a new repetition within a given set, including its quality score and any error flags.
    """
    # Verify the parent set exists
    db_set = crud.get_exercise_set(db, set_id=set_id)
    if not db_set:
        raise HTTPException(
            status_code=404, detail="Set not found to add repetition to"
        )

    return crud.create_repetition(db=db, rep_create=rep_data, set_id=set_id)
