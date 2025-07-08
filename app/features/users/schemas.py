from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    age: int
    address: str


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    age: int
    address: str

    class Config:
        from_attributes = True
