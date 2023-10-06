from datetime import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel


class GameBase(BaseModel):
    winner: str
    loser: str


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    class Config:
        from_attributes = True
