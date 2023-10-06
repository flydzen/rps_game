import asyncio
import datetime
import datetime as dt
from typing import Dict, Set, Optional, List
from uuid import uuid4, UUID
from fastapi import WebSocket
from sqlalchemy.orm import Session

from server.app.db import crud
from server.app.db.schemas import GameCreate
from server.app.enums import PublicCast, Cast
from server.app.schemas.ws import GameStatus, StateResponse

User = str
# each beats the next
CASTS_ORDER = (Cast.ROCK, Cast.SCISSORS, Cast.PAPER)


class Round:
    def __init__(self, index: int):
        self.moves = {}
        self.expiration = dt.datetime.now() + dt.timedelta(seconds=1000)
        self.index = index
        self.draw = None
        self.winner = None

    def add_move(self, login: User, cast: Cast):
        assert dt.datetime.now() <= self.expiration
        self.moves[login] = cast
        if len(self.moves) == 2:
            self.calculate_result()

    def calculate_result(self):
        u1, u2 = self.moves.keys()
        c1, c2 = self.moves[u1], self.moves[u2]
        if c1 == c2:
            self.draw = True
        elif CASTS_ORDER[(CASTS_ORDER.index(c1) + 1) % len(CASTS_ORDER)] == c2:
            self.draw = False
            self.winner = u1
        else:
            self.winner = u2

    @property
    def is_complete(self):
        return self.draw is not None or self.winner is not None


class Game:
    def __init__(self):
        self.game_id = uuid4()
        self.rounds: list[Round] = []
        self.websockets: Dict[User, Optional[WebSocket]] = {}
        self.revenue_requests: Set[User] = set()
        self.terminated: bool = False

    async def add_user(self, db: Session, user: User, websocket: WebSocket):
        self.websockets[user] = websocket
        if len(self.websockets) == 2:
            await self.start_round(db)

    async def revenue_request(self, db: Session, user: User):
        self.revenue_requests.add(user)
        if len(self.revenue_requests) == 2:
            self.revenue_requests = set()
            await self.start_round(db)

    async def add_step(self, db: Session, user: User, cast: Cast):
        last_round = self.rounds[-1]
        last_round.add_move(user, cast)
        if last_round.is_complete:
            await self.notify_finish()
            await self.store_in_db(db)
            if last_round.winner is None:
                run_task(
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

    async def finish_last_round(self, db: Session):
        await self.store_in_db(db)
        await self.notify_finish()

    async def store_in_db(self, db: Session):
        last_round = self.rounds[-1]
        if last_round.winner is None:
            return
        loser = [u for u in self.websockets.keys() if u != last_round.winner][0]
        crud.create_game(db, GameCreate(winner=last_round.winner, loser=loser))

    async def notify_finish(self):
        last_round = self.rounds[-1]
        for user, user_ws in self.websockets.items():
            if user_ws is None:
                continue
            opponent = next(iter([k for k in self.websockets.keys() if k != user]), None)

            if last_round.draw:
                game_status = GameStatus.DRAW
            elif user in last_round.winner:
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

    async def technical_lose(self, db: Session, user):
        if not self.rounds or self.terminated or self.rounds[-1].is_complete:
            return
        self.websockets[user] = None
        self.terminated = True
        last_round = self.rounds[-1]
        last_round.winner = [k for k in self.websockets.keys() if k != user][0]
        last_round.draw = False
        await self.notify_finish()
        await self.store_in_db(db)

    async def schedule_start_new_round(self, db: Session):
        await asyncio.sleep(1)
        await self.start_round(db)

    async def start_round(self, db: Session):
        new_round = Round(len(self.rounds))
        self.rounds.append(new_round)
        await self.notify_in_progress()
        run_task(
            self.scheduled_ttl_check(db, new_round)
        )

    async def scheduled_ttl_check(self, db: Session, last_round: Round):
        rest = last_round.expiration - datetime.datetime.now()
        await asyncio.sleep(rest.seconds)
        await self.ttl_check(db, last_round)

    async def ttl_check(self, db: Session, last_round: Round):
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


class State:
    def __init__(self):
        self.lobby: Game | None = None
        self.games: Dict[UUID, Game] = {}

    def get_free_game(self) -> Game:
        if self.lobby is None:
            self.lobby = Game()
            self.games[self.lobby.game_id] = self.lobby
            return self.lobby
        else:
            game = self.lobby
            self.lobby = None
            return game

    def close_game(self, game: Game):
        if self.lobby == game:
            self.lobby = None
        if game.game_id in self.games:
            del self.games[game.game_id]
        game.terminated = True


def run_task(task):
    loop = asyncio.get_event_loop()
    loop.create_task(task)


state = State()
