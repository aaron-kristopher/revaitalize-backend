from sqlalchemy.orm import Session
from . import models, schemas
from app.security import hash_password

# ==================================
#         USER CRUD Functions
# ==================================

# --- READ (GET) ---


def get_user(db: Session, user_id: int):
    """Fetches a single user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Fetches a single user by their email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Fetches a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


# --- CREATE (POST) ---


def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user with a hashed password."""
    hashed_pass = hash_password(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_pass,
        age=user.age,
        address=user.address,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- UPDATE (PUT) ---


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Updates a user's information."""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None

    # Get the update data from the Pydantic model
    update_data = user_update.model_dump(exclude_unset=True)

    # Loop through the provided data and update the user object
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


# --- DELETE ---


def delete_user(db: Session, user_id: int):
    """Deletes a user by their ID."""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user  # Return the deleted user for confirmation


# ==================================
#       ONBOARDING CRUD Functions
# ==================================


def create_user_onboarding(
    db: Session, onboarding: schemas.OnboardingCreate, user_id: int
):
    # Check if onboarding data already exists for this user
    existing_onboarding = (
        db.query(models.Onboarding).filter(models.Onboarding.user_id == user_id).first()
    )
    if existing_onboarding:
        return None  # Indicate that it already exists

    db_onboarding = models.Onboarding(**onboarding.model_dump(), user_id=user_id)
    db.add(db_onboarding)
    db.commit()
    db.refresh(db_onboarding)
    return db_onboarding


def get_user_onbaording(db: Session, user_id: int):
    """Fetches the onboarding information of a user using the ID"""
    return (
        db.query(models.Onboarding).filter(models.Onboarding.user_id == user_id).first()
    )


def update_user_onboarding(
    db: Session, user_id: int, onboarding_update: schemas.OnboardingUpdate
):
    """Updates a user's onboarding information."""
    db_user_onboarding = get_user_onbaording(db=db, user_id=user_id)

    if not db_user_onboarding:
        return None

    updated_onboarding_data = onboarding_update.model_dump(exclude_unset=True)

    for key, value in updated_onboarding_data.items():
        setattr(db_user_onboarding, key, value)

    db.commit()
    db.refresh(db_user_onboarding)
    return db_user_onboarding


def delete_user_onboarding(db: Session, user_id: int):
    """Deletes a user's onboarding information using the ID"""
    db_user_onboarding = get_user_onbaording(db=db, user_id=user_id)

    if not db_user_onboarding:
        return None

    db.delete(db_user_onboarding)
    db.commit()
    return db_user_onboarding


# ==================================
#     USER PROBLEM CRUD Functions
# ==================================


def create_user_problem(db: Session, problem: schemas.UserProblemCreate, user_id: int):
    db_problem = models.UserProblem(**problem.model_dump(), user_id=user_id)
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
    """Updates a user's problem area information using their ID"""
    db_user_problem = get_user(db=db, user_id=user_id)

    if not db_user_problem:
        return None

    updated_user_problem = user_problem_update.model_dump(exclude_unset=True)

    for key, value in updated_user_problem.items():
        setattr(db_user_problem, key, value)

    db.commit()
    db.refresh(db_user_problem)

    return db_user_problem
