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
from app.security import get_current_active_user, hash_password, verify_password
from . import crud, schemas
from app.features.exercises import crud as exercises_crud

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

    hashed_password: str = hash_password(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)


@router.get("/all", response_model=List[schemas.UserOut])
def get_all_users_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.UserOut)
async def read_users_me(
    current_user: schemas.UserOut = Depends(get_current_active_user),
):
    """
    Fetch the currently authenticated uesr based on their JWT
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user_by_id_route(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


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
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    file_ext = file.filename.split(".")[-1]
    filename = f"user_{user_id}_profile.{file_ext}"
    static_file_path = f"app/static/images/{filename}"
    url_path = f"/static/images/{filename}"

    os.makedirs(os.path.dirname(static_file_path), exist_ok=True)
    with open(static_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

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
            detail=f"User with id {user_id} either does not exist or does not have any onboarding information yet.",
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
    db_user = crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # --- FIX IS HERE ---
    # Convert the frontend identifier (e.g., "hiding_face")
    # to the database format (e.g., "Hiding Face")
    exercise_name_db_format = problem.problem_area.replace("_", " ").title()

    # Find the exercise by its formatted name
    db_exercise = exercises_crud.get_exercise_by_name(db, name=exercise_name_db_format)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with name '{exercise_name_db_format}' not found.",
        )

    # Pass the found exercise_id to the CRUD function
    return crud.create_user_problem(
        db=db, problem=problem, user_id=user_id, exercise_id=db_exercise.id
    )


@router.get("/{user_id}/problems", response_model=List[schemas.UserProblemOut])
def get_problems_for_user_route(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return crud.get_user_problems(db=db, user_id=user_id)


@router.put("/{user_id}/problems", response_model=schemas.UserProblemOut)
def update_problem_for_user(
    user_id: int,
    user_problem_update: schemas.UserProblemUpdate,
    db: Session = Depends(get_db),
):
    user_problem = crud.update_user_problem(
        db=db, user_id=user_id, user_problem_update=user_problem_update
    )

    if not user_problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} either does not exist or does not have any Problem Area information yet.",
        )

    return user_problem


@router.post(
    "/{user_id}/change-password",
    status_code=status.HTTP_200_OK
)
def change_user_password_route(
    user_id: int,
    passwords: schemas.ChangePasswordPayload,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_active_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )

    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify password
    if not verify_password(passwords.current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
        
    # 2. Hash the new password
    new_hashed_password = hash_password(passwords.new_password)
    
    # 3. Call the CRUD function to update it in the database
    crud.update_user_password(db, user_id=user_id, new_hashed_password=new_hashed_password)
    
    return {"message": "Password changed successfully"}