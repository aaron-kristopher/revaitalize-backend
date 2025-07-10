from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session, selectinload
from . import models, schemas

# ==================================
#    SESSION REQUIREMENT CRUD
# ==================================


def get_session_requirement(db: Session, requirement_id: int):
    """Fetches a single session requirement by its ID."""
    return (
        db.query(models.SessionRequirement)
        .filter(models.SessionRequirement.id == requirement_id)
        .first()
    )


def get_user_session_requirements(db: Session, user_id: int):
    """Fetches all session requirements for a specific user."""
    return (
        db.query(models.SessionRequirement)
        .filter(models.SessionRequirement.user_id == user_id)
        .all()
    )


def create_session_requirement(
    db: Session, requirement: schemas.SessionRequirementCreate, user_id: int
):
    """Creates a new SessionRequirement for a user and exercise."""
    # Check for existing requirement for the same user and exercise to avoid duplicates
    existing_req = (
        db.query(models.SessionRequirement)
        .filter(
            models.SessionRequirement.user_id == user_id,
            models.SessionRequirement.exercise_id == requirement.exercise_id,
        )
        .first()
    )

    if existing_req:
        return None  # Return None to indicate a conflict/duplicate

    db_req = models.SessionRequirement(
        number_of_reps=requirement.number_of_reps,
        number_of_sets=requirement.number_of_sets,
        user_id=user_id,
        exercise_id=requirement.exercise_id,
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req


def update_session_requirement(
    db: Session,
    requirement_id: int,
    requirement_update: schemas.SessionRequirementUpdate,
):
    """Updates the reps or sets for an existing session requirement."""
    db_req = get_session_requirement(db, requirement_id=requirement_id)
    if not db_req:
        return None  # Not found

    update_data = requirement_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_req, key, value)

    db.commit()
    db.refresh(db_req)
    return db_req


def delete_session_requirement(db: Session, requirement_id: int):
    """Deletes a session requirement."""
    db_req = get_session_requirement(db, requirement_id=requirement_id)
    if not db_req:
        return None

    db.delete(db_req)
    db.commit()
    return db_req


# ==================================
#          SESSION CRUD
# ==================================


def create_session(db: Session, user_id: int, exercise_id: int):
    """Creates a new Session record, linking a user to an exercise."""
    db_session = models.Session(user_id=user_id, exercise_id=exercise_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_session(db: Session, session_id: int):
    """Fetches a single session by its ID, including its sets and reps."""
    return (
        db.query(models.Session)
        .options(selectinload(models.Session.exercise_sets))
        .filter(models.Session.id == session_id)
        .first()
    )


def get_user_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Fetches all sessions for a specific user."""
    return (
        db.query(models.Session)
        .options(selectinload(models.Session.exercise_sets))
        .filter(models.Session.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_session(db: Session, session_id: int, session_update: schemas.SessionUpdate):
    """Updates a session, typically called when a session ends."""
    db_session = get_session(db, session_id=session_id)
    if not db_session:
        return None

    update_data = session_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_session, key, value)

    # Also set the end time when marking as complete
    if session_update.is_completed:
        db_session.datetime_end = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions_by_date_range(
    db: Session, user_id: int, start: datetime, end: datetime
):
    return (
        db.query(models.Session)
        .options(selectinload(models.Session.exercise_sets))
        .filter(
            models.Session.user_id == user_id,
            models.Session.datetime_start >= start,
            models.Session.datetime_start < end,
        )
        .all()
    )


def get_sessions_today(db: Session, user_id: int):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return get_sessions_by_date_range(db, user_id, start, end)


def get_sessions_yesterday(db: Session, user_id: int):
    now = datetime.now(timezone.utc)
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)
    return get_sessions_by_date_range(db, user_id, start, end)


def get_sessions_this_week(db: Session, user_id: int):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=now.weekday())  # Monday
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return get_sessions_by_date_range(db, user_id, start, end)


def get_sessions_this_month(db: Session, user_id: int):
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        end = now.replace(
            year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    else:
        end = now.replace(
            month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    return get_sessions_by_date_range(db, user_id, start, end)


# ==================================
#        EXERCISE SET CRUD
# ==================================


def create_exercise_set(
    db: Session, set_create: schemas.ExerciseSetCreate, session_id: int
):
    """Creates a new Set record within a Session."""
    db_set = models.ExerciseSet(set_number=set_create.set_number, session_id=session_id)
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set


def get_exercise_set(db: Session, set_id: int):
    """Fetches a single set by its ID."""
    return (
        db.query(models.ExerciseSet)
        .options(selectinload(models.ExerciseSet.repetitions))
        .filter(models.ExerciseSet.id == set_id)
        .first()
    )


def update_exercise_set(
    db: Session, set_id: int, set_update: schemas.ExerciseSetUpdate
):
    """Updates a set's quality score or completion status."""
    db_set = get_exercise_set(db, set_id=set_id)
    if not db_set:
        return None

    update_data = set_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_set, key, value)

    db.commit()
    db.refresh(db_set)
    return db_set


# ==================================
#         REPETITION CRUD
# ==================================


def create_repetition(db: Session, rep_create: schemas.RepetitionCreate, set_id: int):
    """Creates a new Repetition record within a Set."""
    db_rep = models.Repetition(
        set_id=set_id,
        rep_number=rep_create.rep_number,
        rep_quality_score=rep_create.rep_quality_score,
        error_flag=rep_create.error_flag,
        is_completed=True,  # A repetition is complete by definition when it's logged
    )
    db.add(db_rep)
    db.commit()
    db.refresh(db_rep)
    return db_rep


def get_single_repetition(db: Session, set_id: int, repetition_id: int):
    """Fetches one repetition for a specific set."""
    return (
        db.query(models.Repetition)
        .filter(
            models.Repetition.set_id == set_id, models.Repetition.id == repetition_id
        )
        .first()
    )


def get_set_repetitions(db: Session, set_id: int):
    """Fetches all repetitions for a specific set."""
    return db.query(models.Repetition).filter(models.Repetition.set_id == set_id).all()
