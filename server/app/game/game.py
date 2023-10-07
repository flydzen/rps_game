import asyncio
import datetime
from typing import Dict, Optional, Set
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.websockets import WebSocket

from app.db.crud import CRUD
from app.enums import Cast, GameStatus, PublicCast
from app.game.round import Round
from app.game.utils import User
from app.game import utils
from app.schemas.ws import StateResponse


class Game:
    def __init__(self):
        self.game_id = uuid4()
        self.rounds: list[Round] = []
        self.websockets: Dict[User, Optional[WebSocket]] = {}
        self.revenue_requests: Set[User] = set()
        self.terminated: bool = False

    async def add_user(self, db: AsyncSession, user: User, websocket: WebSocket):
        self.websockets[user] = websocket
        if len(self.websockets) == 2:
            await self.start_round(db)

    async def revenue_request(self, db: AsyncSession, user: User):
        self.revenue_requests.add(user)
        if len(self.revenue_requests) == 2:
            self.revenue_requests = set()
            await self.start_round(db)

    async def add_step(self, db: AsyncSession, user: User, cast: Cast):
        last_round = self.rounds[-1]
        last_round.add_move(user, cast)
        if last_round.is_complete:
            await self.notify_finish()
            await self.store_in_db(db)
            if last_round.winner is None:
                utils.run_task(
                    self.schedule_start_new_round(db)
                )
        else:
            await self.notify_in_progress()

    async def notify_in_progress(self):
        last_round = self.rounds[-1]
        for user, user_ws in self.websockets.items():
            if user_ws is None:
                continue
            opponent = [k for k in self.websockets.keys() if k != user][0]
            await user_ws.send_text(
                StateResponse(
                    game_status=GameStatus.IN_PROGRESS,
                    cast_you=PublicCast.from_cast(last_round.moves.get(user, PublicCast.NONE)),
                    cast_opponent=PublicCast.HIDDEN if opponent in last_round.moves else PublicCast.NONE,
                    opponent_name=opponent,
                    deadline=int(last_round.expiration.timestamp()),
                ).model_dump_json()
            )

    async def notify_wait(self):
        for _, user_ws in self.websockets.items():
            if user_ws is None:
                continue
            await user_ws.send_text(
                StateResponse(
                    game_status=GameStatus.WAITING_FOR_OPPONENT,
                ).model_dump_json()
            )

    async def finish_last_round(self, db: AsyncSession):
        await self.store_in_db(db)
        await self.notify_finish()

    async def store_in_db(self, db: AsyncSession):
        last_round = self.rounds[-1]
        if last_round.winner is None:
            return
        loser = [u for u in self.websockets.keys() if u != last_round.winner][0]
        await CRUD.inc_victories(db=db, login=last_round.winner)
        await CRUD.inc_losses(db=db, login=loser)

    async def notify_finish(self):
        last_round = self.rounds[-1]
        for user, user_ws in self.websockets.items():
            if user_ws is None:
                continue
            opponent = next(iter([k for k in self.websockets.keys() if k != user]), None)

            if last_round.draw:
                game_status = GameStatus.DRAW
            elif user == last_round.winner:
                game_status = GameStatus.WIN
            else:
                game_status = GameStatus.LOSE

            await user_ws.send_text(
                StateResponse(
                    game_status=game_status,
                    cast_you=PublicCast.from_cast(last_round.moves.get(user, PublicCast.NONE)),
                    cast_opponent=PublicCast.from_cast(last_round.moves.get(opponent, PublicCast.NONE)),
                    opponent_name=opponent if self.websockets[opponent] else None,
                ).model_dump_json()
            )

    async def technical_lose(self, db: AsyncSession, user):
        if not self.rounds or self.terminated or self.rounds[-1].is_complete:
            return
        self.websockets[user] = None
        self.terminated = True
        last_round = self.rounds[-1]
        last_round.winner = [k for k in self.websockets.keys() if k != user][0]
        last_round.draw = False
        await self.notify_finish()
        await self.store_in_db(db)

    async def schedule_start_new_round(self, db: AsyncSession):
        await asyncio.sleep(1)
        await self.start_round(db)

    async def start_round(self, db: AsyncSession):
        new_round = Round(len(self.rounds))
        self.rounds.append(new_round)
        await self.notify_in_progress()
        utils.run_task(
            self.scheduled_ttl_check(db, new_round)
        )

    async def scheduled_ttl_check(self, db: AsyncSession, last_round: Round):
        rest = last_round.expiration - datetime.datetime.now()
        await asyncio.sleep(rest.seconds)
        await self.ttl_check(db, last_round)

    async def ttl_check(self, db: AsyncSession, last_round: Round):
        if self.terminated is True:
            return
        if last_round.is_complete:
            return

        sleepers = [u for u in self.websockets.keys() if u not in last_round.moves]
        if len(sleepers) == 0:
            return

        last_round.draw = False
        for u in self.websockets.keys():
            if u in last_round.moves:
                last_round.winner = u

        await self.notify_finish()
        await self.store_in_db(db)
