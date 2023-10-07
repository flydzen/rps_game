from datetime import datetime

import pytest
from freezegun import freeze_time

from app.enums import Cast
from app.game.round import Round


class TestRound:
    @freeze_time(datetime(year=2023, month=1, day=1, hour=14))
    def test_first_move(self):
        r = Round(0)

        assert r.expiration == datetime(year=2023, month=1, day=1, hour=14, second=10)

        r.add_move('1', Cast.ROCK)
        assert r.is_complete is False

    @pytest.mark.parametrize(
        'cast1,cast2,exp_draw,exp_winner',
        [
            (Cast.ROCK, Cast.ROCK, True, None),
            (Cast.ROCK, Cast.PAPER, False, '2'),
            (Cast.ROCK, Cast.SCISSORS, False, '1'),
            (Cast.PAPER, Cast.ROCK, False, '1'),
            (Cast.PAPER, Cast.PAPER, True, None),
            (Cast.PAPER, Cast.SCISSORS, False, '2'),
            (Cast.SCISSORS, Cast.ROCK, False, '2'),
            (Cast.SCISSORS, Cast.PAPER, False, '1'),
            (Cast.SCISSORS, Cast.SCISSORS, True, None),
        ]
    )
    def test_complete(self, cast1, cast2, exp_draw, exp_winner):
        r = Round(0)

        r.add_move('1', cast1)
        r.add_move('2', cast2)

        assert r.is_complete is True
        assert r.draw is exp_draw
        assert r.winner == exp_winner
