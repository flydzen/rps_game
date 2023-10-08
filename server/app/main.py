from typing import Annotated, List, Optional

import jwt
import pydantic
from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from websockets.exceptions import ConnectionClosedError

from app.config import JWT_PRIVATE, JWT_PUBLIC
from app.db import schemas
from app.db.crud import CRUD
from app.db.database import Base, engine, get_db
from app.db.models import LeaderBoard
from app.game.state import State
from app.game.game import Game
from app.schemas.http import AuthRequest, UserAuthResponse
from app.schemas.ws import ActionRequest


app = FastAPI()
state = State()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:80',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
        'http://client:8080',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def gen_token_response(user: str) -> Response:
    token = jwt.encode(
        payload={'login': user},
        key=JWT_PRIVATE,
        algorithm='RS256',
    )
    response = Response()
    response.set_cookie(key='session', value=token, httponly=True, secure=True, samesite='none')
    return response


async def authorization(session: Annotated[Optional[str], Cookie()] = None, db: AsyncSession = Depends(get_db)) -> str:
    if session is None:
        raise HTTPException(403)
    try:
        decoded: dict = jwt.decode(session, JWT_PUBLIC, algorithms=["RS256"])
        user_login: str = decoded['login']
        user = await CRUD.get_user(db, user_login)
        if user is None:
            raise HTTPException(403)
        return user.login
    except Exception:
        raise HTTPException(403)


@app.get('/')
async def root():
    return 'Hello world'


@app.post('/users/signup')
async def signup(user: AuthRequest, db: AsyncSession = Depends(get_db)):
    if await CRUD.get_user(db, login=user.login):
        raise HTTPException(409, 'already in use')
    await CRUD.create_user(db, schemas.UserCreate(**user.model_dump()))
    return gen_token_response(user.login)


@app.post('/users/signin')
async def signin(user: AuthRequest, db: AsyncSession = Depends(get_db)):
    if not await CRUD.check_user(db, schemas.UserCreate(**user.model_dump())):
        raise HTTPException(403, 'wrong name/password')
    return gen_token_response(user.login)


@app.post('/users/token')
async def token(
    user: Annotated[Optional[str], Depends(authorization)],
    db: AsyncSession = Depends(get_db)
) -> UserAuthResponse:
    if not await CRUD.get_user(db, login=user):
        raise HTTPException(403)
    return UserAuthResponse(login=user)


@app.delete('/users/token')
async def token():
    response = Response()
    response.delete_cookie('session', httponly=True, secure=True, samesite='none')
    return response


@app.get('/leaderboard')
async def leaderboard(offset: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)) -> List[LeaderBoard]:
    return await CRUD.get_users_results(db, offset=offset, limit=limit)


@app.get('/leaderboard/user/{login}')
async def leaderboard(login: str, db: AsyncSession = Depends(get_db)):
    return await CRUD.get_user_result(db, login)


@app.websocket("/game")
async def websocket_endpoint(
        websocket: WebSocket,
        user: Annotated[Optional[str], Depends(authorization)],
        db: AsyncSession = Depends(get_db),
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
