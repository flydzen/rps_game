from app.game.state import State


class TestState:
    def test_get_game(self):
        state = State()
        games = [
            state.get_free_game()
            for _ in range(4)
        ]
        assert games[0] == games[1]
        assert games[2] == games[3]

        assert games[0] != games[2]
        assert games[1] != games[3]