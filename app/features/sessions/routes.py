from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from typing import List
from enum import Enum

from app.db.database import get_db
from . import crud, schemas
from app.features.users import crud as users_crud
from app.features.exercises import crud as exercises_crud

router = APIRouter(prefix="/users", tags=["Session"])

# ==================================
#    SESSION REQUIREMENT Routes
# ==================================


@router.post(
    "/{user_id}/requirements",
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
    "/{user_id}/requirements", response_model=List[schemas.SessionRequirementOut]
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
    "/{user_id}/requirements/{requirement_id}",
    response_model=schemas.SessionRequirementOut,
)
def update_user_session_requirement(
    user_id: int,
    requirement_id: int,
    requirement_update: schemas.SessionRequirementUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the reps or sets for a specific session requirement.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

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
    "/{user_id}/sessions/start",
    response_model=schemas.SessionOut,
    status_code=status.HTTP_201_CREATED,
)
def start_new_session(
    session: schemas.SessionCreate, user_id: int, db: Session = Depends(get_db)
):
    """
    Starts a new exercise session for a user. The request body must contain
    the user_id and the exercise_id.
    """
    db_user = users_crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User specified for session not found",
        )

    db_exercise = exercises_crud.get_exercise(db, exercise_id=session.exercise_id)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise specified for session not found",
        )

    return crud.create_session(
        db=db, user_id=session.user_id, exercise_id=session.exercise_id
    )


@router.put("/{user_id}/sessions/{session_id}/end", response_model=schemas.SessionOut)
def end_exercise_session(
    session_id: int,
    user_id: int,
    session_update: schemas.SessionUpdate,
    db: Session = Depends(get_db),
):
    """
    Marks a session as complete and updates its final scores.
    The request body can contain the final quality score, error flags, etc.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    ended_session = crud.update_session(
        db, session_id=session_id, session_update=session_update
    )
    if not ended_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return ended_session


@router.get("/{user_id}/sessions/{session_id}", response_model=schemas.SessionOut)
def get_session_details(session_id: int, user_id: int, db: Session = Depends(get_db)):
    """

    Gets all details for a specific session, including its nested sets and repetitions.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return db_session


class SessionTimeFilter(str, Enum):
    today = "today"
    yesterday = "yesterday"
    this_week = "this_week"
    this_month = "this_month"
    all_time = "all_time"


@router.get(
    "/{user_id}/sessions/filter/{time_filter}", response_model=List[schemas.SessionOut]
)
def get_user_sessions_by_time_range(
    user_id: int,
    time_filter: SessionTimeFilter,
    db: Session = Depends(get_db),
):
    """
    Returns sessions for a user based on the selected time filter.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if time_filter == SessionTimeFilter.today:
        return crud.get_sessions_today(db, user_id)
    elif time_filter == SessionTimeFilter.yesterday:
        return crud.get_sessions_yesterday(db, user_id)
    elif time_filter == SessionTimeFilter.this_week:
        return crud.get_sessions_this_week(db, user_id)
    elif time_filter == SessionTimeFilter.this_month:
        return crud.get_sessions_this_month(db, user_id)
    elif time_filter == SessionTimeFilter.all_time:
        return crud.get_all_sessions(db, user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid time filter"
        )


@router.get(
    "/{user_id}/sessions/{session_id}/detail", response_model=schemas.SessionOut
)
def get_session_by_id(user_id: int, session_id: int, db: Session = Depends(get_db)):
    db_user = users_crud.get_user(db=db, user_id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session_by_id(db=db, user_id=user_id, session_id=session_id)

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} does not exist",
        )

    return db_session


# ==================================
#       EXERCISE SET Routes
# ==================================


@router.post(
    "/{user_id}/sessions/{session_id}/sets",
    response_model=schemas.ExerciseSetOut,
    status_code=status.HTTP_201_CREATED,
)
def add_set_to_session(
    session_id: int,
    user_id: int,
    set_data: schemas.ExerciseSetCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a new set record and associates it with a session.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found to add set to",
        )

    return crud.create_exercise_set(db=db, set_create=set_data, session_id=session_id)


@router.get(
    "/{user_id}/sessions/{session_id}/sets/{set_id}",
    response_model=schemas.ExerciseSetOut,
)
def get_exercise_set(
    set_id: int, user_id: int, session_id: int, db: Session = Depends(get_db)
):
    """
    Get exercise set information
    """

    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return crud.get_exercise_set(db=db, set_id=set_id)


@router.put(
    "/{user_id}/sessions/{session_id}/sets/{set_id}",
    response_model=schemas.ExerciseSetOut,
)
def update_exercise_set_details(
    set_id: int,
    user_id: int,
    set_update: schemas.ExerciseSetUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates the details of a specific set (e.g., quality score) after it's completed.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    updated_set = crud.update_exercise_set(db, set_id=set_id, set_update=set_update)
    if updated_set is None:
        raise HTTPException(status_code=404, detail="Set not found")
    return updated_set


# ==================================
#         REPETITION Routes
# ==================================


@router.post(
    "/{user_id}/sessions/{session_id}/sets/{set_id}/repetitions",
    response_model=schemas.RepetitionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_repetition_to_set(
    set_id: int,
    session_id: int,
    user_id: int,
    rep_data: schemas.RepetitionCreate,
    db: Session = Depends(get_db),
):
    """
    Logs a new repetition within a given set, including its quality score and any error flags.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    db_set = crud.get_exercise_set(db, set_id=set_id)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Set not found to add repetition to",
        )

    return crud.create_repetition(db=db, rep_create=rep_data, set_id=set_id)


@router.get("/{user_id}/sessions/{session_id}/sets/{set_id}/repetitions/all")
def get_set_repetitions(
    user_id: int, session_id: int, set_id: int, db: Session = Depends(get_db)
):
    """
    Gets all the repetitions for a given set.
    """

    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    db_set = crud.get_exercise_set(db, set_id=set_id)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Set not found to add repetition to",
        )

    return crud.get_set_repetitions(db=db, set_id=set_id)


@router.get(
    "/{user_id}/sessions/{session_id}/sets/{set_id}/repetitions/{repetition_id}",
    response_model=schemas.RepetitionOut,
)
def get_repetition(
    user_id: int,
    session_id: int,
    set_id: int,
    repetition_id: int,
    db: Session = Depends(get_db),
):
    """
    Gets the repetition for a specific set in a given session.
    """
    db_user = users_crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_session = crud.get_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    db_set = crud.get_exercise_set(db, set_id=set_id)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Set not found to add repetition to",
        )

    return crud.get_single_repetition(db=db, set_id=set_id, repetition_id=repetition_id)
