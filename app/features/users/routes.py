from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

import os
import shutil
from typing import List

from app.db.database import get_db
from app.features.users.models import User
from app.features.users.schemas import UserBase, UserOut


router = APIRouter(prefix="/users", tags=["Users"])


# GET


@router.get("/test-db")
def db_check(db: Session = Depends(get_db)):
    return {"status": "Connection success"}


@router.get("/all", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    if not users:
        return {"data": "There are currently no users saved."}
    return users


@router.get("/{email}", response_model=UserOut)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found",
        )

    return user


@router.get("/{id}", response_model=UserOut)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id_{id} not found.",
        )

    return user


# POST


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserBase, db: Session = Depends(get_db)):
    new_user = User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/upload-profile-picture/{id}")
def upload_profile_picture(
    id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == id).first()

    if not User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    file_ext = file.filename.split(".")[-1]  # type: ignore
    filename = f"user_{id}_profile.{file_ext}"
    filepath = f"static/images/{filename}"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.profile_picture_url = filepath  # type: ignore
    db.commit()
    db.refresh(user)

    return {
        "response": "Profile picture uploaded successfully",
        "profile_filepath": filepath,
    }


# DELETE


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id_{id} not found.",
        )

    user.delete()
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# UPDATE


@router.put("/{id}", response_model=UserOut)
def update_user(id: int, updated_user: UserBase, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id_{id} not found.",
        )

    # for key, value in updated_user.model_dump().items():
    #     setattr(user, key, value)
    user.update(updated_user.model_dump(), synchronize_session=False)  # type: ignore

    db.commit()

    return user.first()
