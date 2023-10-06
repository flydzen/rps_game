from sqlalchemy import and_, select, func, union_all, values, literal
from sqlalchemy.orm import Session
import hashlib

from . import models, schemas
from .models import LeaderBoard
from .schemas import GameCreate, User
from ..config import SALT
from functools import reduce


def pwd_hash(pwd: str):
    steps = [
        lambda x: (SALT + x),
        lambda x: hashlib.md5(x).hexdigest(),
        lambda x: hashlib.md5(x).hexdigest(),
        lambda x: hashlib.sha256(x).hexdigest(),
    ]
    return reduce(lambda res, f: f(res).encode('utf-8'), steps, pwd).decode()


def get_users_results(db: Session, offset: int = 0, limit: int = 20):
    sub_wins = db.query(
        models.User.login.label('login'),
        func.count(models.Game.winner).label('wins'),
        literal(0).label('losses')
    ) \
        .join(models.Game, models.User.login == models.Game.winner) \
        .group_by(models.User.login)

    sub_loses = db.query(
        models.User.login.label('login'),
        literal(0).label('wins'),
        func.count(models.Game.loser).label('losses')
    ) \
        .join(models.Game, models.User.login == models.Game.loser) \
        .group_by(models.User.login)

    union_query = union_all(sub_wins, sub_loses)

    final_query = db.query(
        union_query.c.login,
        func.sum(union_query.c.wins).label('wins'),
        func.sum(union_query.c.losses).label('losses')
    ) \
        .group_by(union_query.c.login) \
        .order_by(func.sum(union_query.c.wins).desc()) \
        .offset(offset) \
        .limit(limit)

    result = final_query.all()
    return [LeaderBoard.from_args(i, *row) for i, row in enumerate(result, start=offset)]


def get_user_result(db: Session, user: User):
    wins_subquery = db.query(func.count().label('wins')) \
        .filter(models.Game.winner == user.login) \
        .subquery()

    loses_subquery = db.query(func.count().label('loses')) \
        .filter(models.Game.loser == user.login) \
        .subquery()

    final_query = db.query(wins_subquery.c.wins, loses_subquery.c.loses)

    db.query(models.User.login).filter(models.Game).count()

    return LeaderBoard.from_args(0, user.login, *final_query.one())


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_hash(user.password)
    db_user = models.User(login=user.login, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def check_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_hash(user.password)
    print(hashed_password)
    return db.query(models.User).filter(
        and_(
            models.User.login == user.login,
            models.User.hashed_password == hashed_password,
        )
    ).first() is not None


def check_login(db: Session, login: str):
    return db.query(models.User).filter_by(login=login).first() is not None


def create_game(db: Session, game: GameCreate):
    db_item = models.Game(**game.model_dump())
    db.add(db_item)
    db.commit()
    return db.refresh(db_item)
