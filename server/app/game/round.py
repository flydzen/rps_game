import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Cast
from app.game.utils import User


# each beats the next
CASTS_ORDER = (Cast.ROCK, Cast.SCISSORS, Cast.PAPER)
TTL = 10  # seconds


class Round:
    def __init__(self, index: int):
        self.moves = {}
        self.expiration = dt.datetime.now() + dt.timedelta(seconds=TTL)
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
            self.draw = False
            self.winner = u2

    @property
    def is_complete(self):
        return self.draw is not None or self.winner is not None
