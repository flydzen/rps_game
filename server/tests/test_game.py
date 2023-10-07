import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.enums import GameStatus, PublicCast
from app.game.game import Game
from app.game.round import Round
from app.db.crud import CRUD
from app.schemas.ws import StateResponse


@pytest.fixture
def game_with_round() -> Game:
    game = Game()
    game.websockets = {'u1': AsyncMock, 'u2': AsyncMock}
    game.rounds = [Round(0)]
    return game


@pytest.fixture
def db():
    return MagicMock()


@pytest.mark.asyncio
async def test_store_in_db_when_victory(db, game_with_round, mocker):
    game_with_round.rounds[0].winner = 'u1'
    game_with_round.rounds[0].draw = False

    mock_losses, mock_victories = AsyncMock(), AsyncMock()

    mocker.patch.object(CRUD, 'inc_losses', side_effect=mock_losses)
    mocker.patch.object(CRUD, 'inc_victories', side_effect=mock_victories)

    await game_with_round.store_in_db(db)

    mock_victories.assert_called_once_with(db=db, login='u1')
    mock_losses.assert_called_once_with(db=db, login='u2')
