from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_session
from ..deps import current_user
from ..games import coinflip
from ..models import GameRound, User
from ..services import wallet as wallet_service

router = APIRouter(prefix="/games", tags=["games"])


class CoinflipIn(BaseModel):
    choice: Literal["heads", "tails"]
    bet: int = Field(ge=settings.min_bet, le=settings.max_bet)
    request_id: str | None = Field(default=None, max_length=64)  # захист від повторного відправлення


def _out(rnd: GameRound, balance: int) -> dict:
    return {
        "round_id": rnd.id, "pick": rnd.pick, "result": rnd.outcome,
        "won": rnd.payout > 0, "bet": rnd.bet, "payout": rnd.payout, "balance": balance,
    }


@router.post("/coinflip")
async def play_coinflip(
    data: CoinflipIn,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    wallet = await wallet_service.lock_wallet(session, user.id)  # усі ходи гравця йдуть по черзі

    rid = f"{user.id}:{data.request_id}" if data.request_id else None
    if rid:
        prev = await session.scalar(select(GameRound).where(GameRound.request_id == rid))
        if prev:  # той самий запит удруге: повертаємо збережений результат
            return _out(prev, wallet.balance)

    if wallet.balance < data.bet:
        raise HTTPException(400, "Недостатньо монет")

    result = coinflip.flip()
    won = result == data.choice
    rnd = GameRound(
        user_id=user.id, game="coinflip", bet=data.bet,
        payout=coinflip.payout(data.bet) if won else 0,
        pick=data.choice, outcome=result, request_id=rid,
    )
    session.add(rnd)
    await session.flush()

    await wallet_service.apply(session, user.id, -data.bet, "bet", ref=str(rnd.id))
    if won:
        await wallet_service.apply(session, user.id, rnd.payout, "win", ref=str(rnd.id))
    await session.commit()
    return _out(rnd, wallet.balance)
