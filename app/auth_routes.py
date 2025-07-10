from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
# Import the functions we just created in security.py
from app.security import authenticate_user, create_access_token

# Create a new router for authentication endpoints
router = APIRouter(tags=["Authentication"])

@router.post("/token")
def login_for_access_token(
    # This special dependency automatically gets the 'username' and 'password'
    # from the incoming form data. Your frontend correctly sends 'username'.
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    This is the main login endpoint. It receives credentials, authenticates the user,
    and returns a JWT access token.
    """
    # Call our authentication helper function. form_data.username contains the email.
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    
    # If authenticate_user returns False, the login details were incorrect.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If authentication is successful, create a new access token.
    # The "sub" (subject) of the token is typically the user's unique identifier (email).
    access_token = create_access_token(data={"sub": user.email})
    
    # Return the token and the user object, as your frontend expects.
    return {"access_token": access_token, "token_type": "bearer", "user": user}