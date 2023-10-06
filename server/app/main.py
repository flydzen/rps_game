from typing import Annotated, Optional, List

import pydantic
import sqlalchemy.engine.row
from fastapi import FastAPI, WebSocket, HTTPException, Response, WebSocketDisconnect, WebSocketException, Cookie, \
    Depends
from sqlalchemy.orm import Session
from websockets.exceptions import ConnectionClosedError
from fastapi.middleware.cors import CORSMiddleware
import jwt
from .config import JWT_PRIVATE, JWT_PUBLIC

from server.app.schemas.ws import ActionRequest
from .db import schemas, crud
from .db.database import get_db
from .db.models import LeaderBoard
from .db.schemas import User as UserDB
from .game_logic import state, Game
from server.app.schemas.http import AuthRequest, UserAuthResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://localhost:80',
        'http://localhost:8080',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def gen_token_response(user: str) -> Response:
    token = jwt.encode(
        payload={'login': user},
        key=JWT_PRIVATE,
        algorithm='RS256',
    )
    response = Response()
    response.set_cookie(key='session', value=token, httponly=True, secure=True, samesite='none')
    return response


def authorization(session: Annotated[Optional[str], Cookie()] = None) -> str:
    if session is None:
        raise HTTPException(403)
    try:
        decoded: dict = jwt.decode(session, JWT_PUBLIC, algorithms=["RS256"])
        user_login: str = decoded['login']
    except Exception:
        raise HTTPException(403)
    return user_login


@app.get('/')
async def root():
    return 'Hello world'


@app.post('/users/signup')
async def signup(user: AuthRequest, db: Session = Depends(get_db)):
    if crud.check_login(db, login=user.login):
        raise HTTPException(409, 'already in use')
    crud.create_user(db, schemas.UserCreate(**user.model_dump()))
    return gen_token_response(user.login)


@app.post('/users/signin')
async def signin(user: AuthRequest, db: Session = Depends(get_db)):
    if not crud.check_user(db, schemas.UserCreate(**user.model_dump())):
        raise HTTPException(403, 'wrong name/password')
    return gen_token_response(user.login)


@app.post('/users/token')
async def token(user: Annotated[Optional[str], Depends(authorization)]) -> UserAuthResponse:
    return UserAuthResponse(login=user)


@app.delete('/users/token')
async def token():
    response = Response()
    response.delete_cookie('session', httponly=True, secure=True, samesite='none')
    return response


@app.get('/leaderboard')
async def leaderboard(offset: int = 0, limit: int = 20, db: Session = Depends(get_db)) -> List[LeaderBoard]:
    return crud.get_users_results(db, offset=offset, limit=limit)


@app.get('/leaderboard/user/{login}')
async def leaderboard(login: str, db: Session = Depends(get_db)):
    results = crud.get_user_result(db, UserDB(login=login))
    print(results)
    return results


@app.websocket("/game")
async def websocket_endpoint(
        websocket: WebSocket,
        user: Annotated[Optional[str], Depends(authorization)],
        db: Session = Depends(get_db),
):
    try:
        await websocket.accept()
    except (WebSocketDisconnect, WebSocketException):
        await websocket.close()
        return
    game: Game = state.get_free_game()
    try:
        await game.add_user(db, user, websocket)

        # ок, у нас есть игра
        while True:
            data = await websocket.receive_json()
            try:
                action = ActionRequest.model_validate(data)
                if action.cast:
                    await game.add_step(db, user, action.cast)
                if action.revenge:
                    await game.revenue_request(db, user)
            except pydantic.ValidationError as e:
                print(e)
    except (WebSocketDisconnect, WebSocketException, ConnectionClosedError):
        await game.technical_lose(db, user)
        return
