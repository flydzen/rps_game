from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    login = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    victories = Column(Integer, default=0)
    losses = Column(Integer, default=0)


class LeaderBoard(BaseModel):
    position: int
    login: str
    victories: int
    losses: int

    @classmethod
    def from_args(cls, *row):
        return cls(**{key: row[i] for i, key in enumerate(cls.model_fields.keys())})
