from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Response,
)
from sqlalchemy.orm import Session
from typing import List
import shutil
import os


from app.db.database import get_db
from . import crud, schemas

router = APIRouter(prefix="/users", tags=["Users"])

# ==================================
#         USER API Routes
# ==================================


@router.post(
    "/create", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED
)
def create_user_route(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)


@router.get("/all", response_model=List[schemas.UserOut])
def get_all_users_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user_by_id_route(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user

@router.get("/{email}", response_model=schemas.UserOut)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db=db, email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found.",
        )

    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user_route(
    user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)
):
    updated_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    deleted_user = crud.delete_user(db, user_id=user_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==================================
#   PROFILE PICTURE API Routes
# ==================================


@router.post("/upload-profile-picture/{user_id}", response_model=schemas.UserOut)
def upload_profile_picture_route(
    user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    # First, check if user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Define file path and save the file
    file_ext = file.filename.split(".")[-1]
    filename = f"user_{user_id}_profile.{file_ext}"

    # The path should be relative to the static directory mount point
    # We mount `/static` to the `app/static` folder in main.py
    # So the URL will be `/static/images/{filename}`
    # The physical path is `app/static/images/{filename}`
    static_file_path = f"app/static/images/{filename}"
    url_path = f"/static/images/{filename}"

    os.makedirs(os.path.dirname(static_file_path), exist_ok=True)
    with open(static_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update user in the database with the URL path
    return crud.update_user_profile_picture(db, user_id=user_id, file_path=url_path)


# ==================================
#   ONBOARDING & PROBLEM API Routes
# ==================================


@router.post(
    "/{user_id}/onboarding",
    response_model=schemas.OnboardingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_onboarding_for_user_route(
    user_id: int, onboarding: schemas.OnboardingCreate, db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    created_onboarding = crud.create_user_onboarding(
        db=db, onboarding=onboarding, user_id=user_id
    )
    if created_onboarding is None:
        raise HTTPException(
            status_code=409, detail="Onboarding data already exists for this user"
        )

    return created_onboarding


@router.get("/{user_id}/onboarding", response_model=schemas.OnboardingOut)
def get_user_onboarding(user_id: int, db: Session = Depends(get_db)):
    db_user_onboarding = crud.get_user_onbaording(db=db, user_id=user_id)

    if not db_user_onboarding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} either does not exist or does not have any onboarding information yet.",
        )

    return db_user_onboarding


@router.put("/{user_id}/onboarding", response_model=schemas.OnboardingOut)
def update_user_onboarding(
    user_id: int,
    onboarding_update: schemas.OnboardingUpdate,
    db: Session = Depends(get_db),
):
    db_user_onboarding = crud.get_user_onbaording(db=db, user_id=user_id)

    updated_user_onboarding = crud.update_user_onboarding(
        db=db, user_id=user_id, onboarding_update=onboarding_update
    )

    if not updated_user_onboarding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} either does not exist or does not have any onboarding information yet.",
        )

    return updated_user_onboarding


@router.delete("/{user_id}/onboarding")
def delete_user_onboarding(user_id: int, db: Session = Depends(get_db)):
    db_user_onboarding = crud.delete_user_onboarding(db=db, user_id=user_id)

    if not db_user_onboarding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with id {user_id} either does not exist or does not have any onboarding information yet."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{user_id}/problems",
    response_model=schemas.UserProblemOut,
    status_code=status.HTTP_201_CREATED,
)
def create_problem_for_user_route(
    user_id: int, problem: schemas.UserProblemCreate, db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return crud.create_user_problem(db=db, problem=problem, user_id=user_id)


@router.get("/{user_id}/problems", response_model=List[schemas.UserProblemOut])
def get_problems_for_user_route(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return crud.get_user_problems(db=db, user_id=user_id)

@router.put("/{user_id}/problems", response_model=schemas.UserProblemOut)
def update_problem_for_user(user_id: int, user_problem_update: schemas.UserProblemUpdate, db: Session = Depends(get_db)):

    user_problem = crud.update_user_problem(db=db, user_id=user_id, user_problem_update=user_problem_update)

    if not user_problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User with id {id} either does not exist or does not have any Problem Area information yet."
                            )

    return user_problem
