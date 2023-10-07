import hashlib
from functools import reduce

from sqlalchemy import func, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models, schemas
from app.config import SALT


def pwd_hash(pwd: str):
    steps = [
        lambda x: (SALT + x),
        lambda x: hashlib.md5(x).hexdigest(),
        lambda x: hashlib.md5(x).hexdigest(),
        lambda x: hashlib.sha256(x).hexdigest(),
    ]
    return reduce(lambda res, f: f(res).encode('utf-8'), steps, pwd).decode()


class CRUD:
    @staticmethod
    async def get_users_results(db: AsyncSession, offset: int = 0, limit: int = 20):
        stmt = select(
            func.rank().over(order_by=models.User.victories.desc()),
            models.User.login,
            models.User.victories,
            models.User.losses,
        ).order_by(
            models.User.victories.desc()
        ).offset(offset).limit(limit)

        result = (await db.execute(stmt)).all()
        return [models.LeaderBoard.from_args(*res) for res in result]

    @staticmethod
    async def get_user_result(db: AsyncSession, login: str):
        cte1 = select(
            models.User.login, models.User.victories, models.User.losses
        ).filter_by(login=login).cte('cte1')
        cte2 = select(
            1 + func.count(models.User.victories).label('place')
        ).where(models.User.victories > select(cte1.c.victories).scalar_subquery()).cte('cte2')
        stmt = select(cte2, cte1).join(cte1, literal(True))

        result = (await db.execute(stmt)).first()
        if result:
            return models.LeaderBoard.from_args(*result)
        return None

    @staticmethod
    async def create_user(db: AsyncSession, user: schemas.UserCreate):
        hashed_password = pwd_hash(user.password)
        db_user = models.User(login=user.login, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def check_user(db: AsyncSession, user: schemas.UserCreate):
        hashed_password = pwd_hash(user.password)

        stmt = select(models.User).filter_by(login=user.login, hashed_password=hashed_password)
        result = await db.execute(stmt)
        return result.scalar_one() is not None

    @staticmethod
    async def inc_victories(db: AsyncSession, login: str):
        await db.execute(
            update(models.User)
            .filter_by(login=login)
            .values(victories=models.User.victories + 1)
        )
        await db.commit()

    @staticmethod
    async def inc_losses(db: AsyncSession, login: str):
        await db.execute(
            update(models.User)
            .filter_by(login=login)
            .values(losses=models.User.losses + 1)
        )
        await db.commit()

    @staticmethod
    async def get_user(db: AsyncSession, login: str):
        stmt = select(models.User).filter_by(login=login)
        result = await db.execute(stmt)
        return result.scalar()
