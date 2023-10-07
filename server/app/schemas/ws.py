from typing import Optional

from pydantic import BaseModel

from app.enums import Cast, GameStatus, PublicCast


class ActionRequest(BaseModel):
    cast: Optional[Cast] = None
    revenge: Optional[bool] = None


class StateResponse(BaseModel):
    game_status: GameStatus
    cast_you: PublicCast = PublicCast.NONE
    cast_opponent: PublicCast = PublicCast.NONE
    opponent_name: Optional[str] = None
    deadline: Optional[int] = None
