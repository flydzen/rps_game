from typing import Dict
from uuid import UUID

from app.game.game import Game


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
