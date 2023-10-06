from enum import Enum


class GameStatus(Enum):
    WAITING_FOR_OPPONENT = 'waiting_for_opponent'
    IN_PROGRESS = 'in_progress'
    WIN = 'win'
    LOSE = 'lose'
    DRAW = 'draw'


class Cast(Enum):
    ROCK = 'rock'
    PAPER = 'paper'
    SCISSORS = 'scissors'


class PublicCast(Enum):
    ROCK = 'rock'
    PAPER = 'paper'
    SCISSORS = 'scissors'
    NONE = 'none'
    HIDDEN = 'hidden'

    @staticmethod
    def from_cast(value: Cast):
        return PublicCast(value.value)
