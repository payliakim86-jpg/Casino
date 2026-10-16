from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_session
from ..deps import current_user
from ..models import DailyBonus, LedgerEntry, User, Wallet
from ..services import wallet as wallet_service

router = APIRouter(tags=["wallet"])


def bonus_amount(streak: int) -> int:
    return settings.bonus_base + settings.bonus_step * (min(streak, settings.bonus_max_streak) - 1)


async def bonus_state(session: AsyncSession, user_id: int) -> dict:
    today = datetime.now(timezone.utc).date()
    row = await session.get(DailyBonus, user_id)
    if row and row.last_claim == today:
        return {"can_claim": False, "streak": row.streak, "amount": bonus_amount(row.streak + 1)}
    continues = row and row.last_claim == today - timedelta(days=1)
    streak = row.streak + 1 if continues else 1
    return {"can_claim": True, "streak": streak, "amount": bonus_amount(streak)}


@router.get("/me")
async def me(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    wallet = await session.get(Wallet, user.id)
    return {
        "nickname": user.nickname,
        "balance": wallet.balance,
        "bonus": await bonus_state(session, user.id),
        "limits": {
            "min_bet": settings.min_bet,
            "max_bet": settings.max_bet,
            "coinflip_multiplier": settings.coinflip_payout_bp / 10000,
        },
    }


@router.post("/bonus/claim")
async def claim_bonus(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    await wallet_service.lock_wallet(session, user.id)  # захист від подвійного кліку
    state = await bonus_state(session, user.id)
    if not state["can_claim"]:
        raise HTTPException(400, "Бонус на сьогодні вже отримано")

    today = datetime.now(timezone.utc).date()
    row = await session.get(DailyBonus, user.id)
    if row:
        row.streak, row.last_claim = state["streak"], today
    else:
        session.add(DailyBonus(user_id=user.id, last_claim=today, streak=state["streak"]))
    await wallet_service.apply(
        session, user.id, state["amount"], "daily_bonus", ref=str(today),
        key=f"bonus:{user.id}:{today}",
    )
    await session.commit()
    return await me(user, session)


@router.get("/ledger")
async def ledger(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    rows = await session.scalars(
        select(LedgerEntry).where(LedgerEntry.user_id == user.id)
        .order_by(LedgerEntry.id.desc()).limit(50)
    )
    return [
        {"amount": r.amount, "balance_after": r.balance_after, "type": r.type, "at": r.created_at}
        for r in rows
    ]
