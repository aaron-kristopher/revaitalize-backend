from typing import Optional
from pydantic import BaseModel, EmailStr

# --- User Schemas ---


# Schema for data required to CREATE a user
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    age: int
    address: str


# Schema for data required to UPDATE a user
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    address: Optional[str] = None


# Schema for data returned FROM the API (never includes the password)
class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    age: int
    address: str
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True  # Formerly orm_mode = True


# --- Onboarding Schemas ---
class OnboardingBase(BaseModel):
    primary_goal: str
    pain_score: int
    preferred_schedule: int


class OnboardingCreate(OnboardingBase):
    pass


class OnboardingUpdate(BaseModel):
    primary_goal: Optional[str] = None
    pain_score: Optional[int] = None
    preferred_schedule: Optional[int] = None


class OnboardingOut(OnboardingBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# --- UserProblem Schemas ---
class UserProblemBase(BaseModel):
    problem_area: str


class UserProblemCreate(UserProblemBase):
    pass


class UserProblemOut(UserProblemBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserProblemUpdate(BaseModel):
    problem_area: Optional[str] = None
