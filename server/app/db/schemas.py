from pydantic import BaseModel


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    victories: int
    losses: int

    class Config:
        from_attributes = True
