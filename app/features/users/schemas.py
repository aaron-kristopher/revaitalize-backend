from typing import Optional
from pydantic import BaseModel, EmailStr


# --- Forward declaration to handle circular dependencies ---
class OnboardingOut(BaseModel):
    id: int
    user_id: int
    primary_goal: str
    pain_score: int
    preferred_schedule: int

    class Config:
        from_attributes = True


# --- User Schemas ---


# Schema for data required to CREATE a user
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    age: int
    address: str
    sex: str
    contact_number: str


# Schema for data required to UPDATE a user
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    address: Optional[str] = None
    sex: Optional[str] = None
    contact_number: Optional[str] = None


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    age: int
    address: str
    sex: str
    contact_number: str
    profile_picture_url: Optional[str] = None

    onboarding_data: Optional[OnboardingOut] = None

    class Config:
        from_attributes = True


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
