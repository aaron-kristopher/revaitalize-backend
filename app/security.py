from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Import our updated settings object from the config file
from app.core.config import settings
# Import the user CRUD functions to look up users in the database
from app.features.users import crud as users_crud

# --- 1. Password Hashing Setup ---
# This sets up the context for hashing and verifying passwords using the bcrypt algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)


# --- 2. JWT Token Configuration ---
# This object tells FastAPI where the client should go to get a token ("tokenUrl").
# FastAPI will use this to automatically generate documentation for the login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    """
    Creates a new JWT access token using the data provided.
    The 'sub' (subject) of the token is typically the user's email or ID.
    """
    to_encode = data.copy()
    # Calculate the expiration time for the token from our settings.
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode the token with our secret key and algorithm from settings.
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# --- 3. User Authentication Function ---
def authenticate_user(db: Session, email: str, password: str):
    """
    The core login logic. It finds a user by their email and then verifies their password.
    
    This function is the bridge between the login form and the database.
    
    Returns the user object on success, or False on failure.
    """
    # Step A: Find the user in the database by their email address.
    user = users_crud.get_user_by_email(db, email=email)
    
    # Step B: If no user is found with that email, authentication fails immediately.
    if not user:
        return False
        
    # Step C: If a user is found, verify their provided password against the hashed password stored in the database.
    if not verify_password(password, user.hashed_password):
        return False
        
    # Step D: If both the user exists and the password is correct, return the full user object.
    return user