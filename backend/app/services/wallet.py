"""Єдине місце, де змінюється баланс. Ігри викликають лише apply()."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import LedgerEntry, Wallet


class InsufficientFunds(Exception):
    pass


async def lock_wallet(session: AsyncSession, user_id: int) -> Wallet:
    # FOR UPDATE блокує рядок у Postgres, тож паралельні запити йдуть по черзі
    return await session.scalar(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    )


async def apply(
    session: AsyncSession,
    user_id: int,
    amount: int,
    type_: str,
    ref: str | None = None,
    key: str | None = None,
) -> LedgerEntry:
    """Змінює баланс на amount і пише запис у леджер. Викликач робить commit."""
    if key:
        existing = await session.scalar(
            select(LedgerEntry).where(LedgerEntry.idempotency_key == key)
        )
        if existing:  # повторний запит з тим самим ключем не дублює операцію
            return existing

    wallet = await lock_wallet(session, user_id)
    if wallet.balance + amount < 0:
        raise InsufficientFunds
    wallet.balance += amount

    entry = LedgerEntry(
        user_id=user_id,
        amount=amount,
        balance_after=wallet.balance,
        type=type_,
        ref=ref,
        idempotency_key=key,
    )
    session.add(entry)
    await session.flush()
    return entry
