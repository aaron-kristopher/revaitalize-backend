from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.features.users import crud as users_crud

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    """
    Creates a new JWT access token using the data provided.
    The 'sub' (subject) of the token is typically the user's email or ID.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    """
    The core login logic. It finds a user by their email and then verifies their password.

    This function is the bridge between the login form and the database.

    Returns the user object on success, or False on failure.
    """
    user = users_crud.get_user_by_email(db, email=email)

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def get_current_active_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Dependency to get the current user from a JWT token.
    This will be used to protect routes.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub", "Sub is empty")

        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_crud.get_user_by_email(db, email=email)

    if user is None:
        raise credentials_exception

    return user

