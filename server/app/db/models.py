from uuid import uuid4

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"

    login = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)


class Game(Base):
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    winner = Column(String, ForeignKey("users.login"))
    loser = Column(String, ForeignKey("users.login"))
    created_at = Column(DateTime, server_default=func.now())


class LeaderBoard(BaseModel):
    position: int
    login: str
    wins: int
    loses: int

    @classmethod
    def from_args(cls, *row):
        return cls(**{key: row[i] for i, key in enumerate(cls.model_fields.keys())})
