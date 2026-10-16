from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_session
from ..models import User, Wallet
from ..security import create_token, hash_password, verify_password
from ..services import wallet as wallet_service

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    nickname: str = Field(min_length=3, max_length=24, pattern=r"^[\w\-]+$")
    password: str = Field(min_length=6, max_length=64)


class TokenOut(BaseModel):
    token: str


@router.post("/register", response_model=TokenOut)
async def register(data: Credentials, session: AsyncSession = Depends(get_session)):
    taken = await session.scalar(
        select(User.id).where(func.lower(User.nickname) == data.nickname.lower())
    )
    if taken:
        raise HTTPException(409, "Цей нік уже зайнятий")

    user = User(nickname=data.nickname, password_hash=hash_password(data.password))
    session.add(user)
    await session.flush()
    session.add(Wallet(user_id=user.id, balance=0))
    await session.flush()
    await wallet_service.apply(session, user.id, settings.start_balance, "signup")
    await session.commit()
    return TokenOut(token=create_token(user.id))


@router.post("/login", response_model=TokenOut)
async def login(data: Credentials, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(
        select(User).where(func.lower(User.nickname) == data.nickname.lower())
    )
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Невірний нік або пароль")
    return TokenOut(token=create_token(user.id))
