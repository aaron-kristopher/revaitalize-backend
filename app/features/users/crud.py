from sqlalchemy.orm import Session, selectinload
from . import models, schemas

# ==================================
#         USER CRUD Functions
# ==================================


def get_user(db: Session, user_id: int):
    """Fetches a single user by their ID, eagerly loading their onboarding data."""
    return (
        db.query(models.User)
        .options(selectinload(models.User.onboarding_data))
        .filter(models.User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str):
    """Fetches a single user by their email, eagerly loading their onboarding data."""
    return (
        db.query(models.User)
        .options(selectinload(models.User.onboarding_data))
        .filter(models.User.email == email)
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Fetches a list of users with pagination, eagerly loading their onboarding data."""
    return (
        db.query(models.User)
        .options(selectinload(models.User.onboarding_data))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """Creates a new user with a hashed password."""
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        age=user.age,
        address=user.address,
        sex=user.sex,
        contact_number=user.contact_number,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Updates a user's information."""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_profile_picture(db: Session, user_id: int, file_path: str):
    """Updates the profile picture URL for a user."""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    db_user.profile_picture_url = file_path
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    """Deletes a user by their ID."""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user


# ==================================
#       ONBOARDING CRUD Functions
# ==================================


def create_user_onboarding(
    db: Session, onboarding: schemas.OnboardingCreate, user_id: int
):
    existing_onboarding = (
        db.query(models.Onboarding).filter(models.Onboarding.user_id == user_id).first()
    )
    if existing_onboarding:
        return None
    db_onboarding = models.Onboarding(**onboarding.model_dump(), user_id=user_id)
    db.add(db_onboarding)
    db.commit()
    db.refresh(db_onboarding)
    return db_onboarding


def get_user_onbaording(db: Session, user_id: int):
    return (
        db.query(models.Onboarding).filter(models.Onboarding.user_id == user_id).first()
    )


def update_user_onboarding(
    db: Session, user_id: int, onboarding_update: schemas.OnboardingUpdate
):
    db_user_onboarding = get_user_onbaording(db=db, user_id=user_id)
    if not db_user_onboarding:
        return None
    updated_onboarding_data = onboarding_update.model_dump(exclude_unset=True)
    for key, value in updated_onboarding_data.items():
        setattr(db_user_onboarding, key, value)
    db.commit()
    db.refresh(db_user_onboarding)
    return db_user_onboarding


def update_onboarding_custom_days(db: Session, user_id: int, days: list[int]):
    """Validate and update onboarding.custom_allowed_days for a user.

    - Ensures onboarding exists
    - Ensures all days are in [0,6]
    - Ensures len(days) matches preferred_schedule
    - Stores sorted values
    """
    db_user_onboarding = get_user_onbaording(db=db, user_id=user_id)
    if not db_user_onboarding:
        return None, "Onboarding not found"

    if any((not isinstance(d, int)) or d < 0 or d > 6 for d in days):
        return None, "custom_allowed_days must contain integers in range 0–6"

    if len(days) != db_user_onboarding.preferred_schedule:
        return None, (
            f"custom_allowed_days length ({len(days)}) must equal preferred_schedule "
            f"({db_user_onboarding.preferred_schedule})"
        )

    # Optional: ensure distinct values
    if len(set(days)) != len(days):
        return None, "custom_allowed_days must not contain duplicates"

    db_user_onboarding.custom_allowed_days = sorted(days)
    db.commit()
    db.refresh(db_user_onboarding)
    return db_user_onboarding, None


def delete_user_onboarding(db: Session, user_id: int):
    db_user_onboarding = get_user_onbaording(db=db, user_id=user_id)
    if not db_user_onboarding:
        return None
    db.delete(db_user_onboarding)
    db.commit()
    return db_user_onboarding


# ==================================
#     USER PROBLEM CRUD Functions
# ==================================


# --- FIX IS HERE ---
def create_user_problem(
    db: Session, problem: schemas.UserProblemCreate, user_id: int, exercise_id: int
):
    # Now includes exercise_id
    db_problem = models.UserProblem(
        **problem.model_dump(), user_id=user_id, exercise_id=exercise_id
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem


def get_user_problems(db: Session, user_id: int):
    return (
        db.query(models.UserProblem).filter(models.UserProblem.user_id == user_id).all()
    )


def update_user_problem(
    db: Session, user_id: int, user_problem_update: schemas.UserProblemUpdate
):
    db_user_problem = get_user(db=db, user_id=user_id)
    if not db_user_problem:
        return None
    updated_user_problem = user_problem_update.model_dump(exclude_unset=True)
    for key, value in updated_user_problem.items():
        setattr(db_user_problem, key, value)
    db.commit()
    db.refresh(db_user_problem)
    return db_user_problem


def update_user_password(db: Session, user_id: int, new_hashed_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    db_user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(db_user)
    return db_user
