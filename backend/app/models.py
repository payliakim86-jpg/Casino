from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Wallet(Base):
    """Кеш поточного балансу. Джерело правди: таблиця ledger."""

    __tablename__ = "wallets"
    __table_args__ = (CheckConstraint("balance >= 0", name="balance_non_negative"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    balance: Mapped[int] = mapped_column(BigInteger, default=0)


class LedgerEntry(Base):
    """Журнал усіх змін балансу. Записи ніколи не редагуються і не видаляються."""

    __tablename__ = "ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[int] = mapped_column(BigInteger)  # + виграш/бонус, - ставка
    balance_after: Mapped[int] = mapped_column(BigInteger)
    type: Mapped[str] = mapped_column(String(20))  # signup, daily_bonus, bet, win
    ref: Mapped[str | None] = mapped_column(String(64), default=None)  # id раунду тощо
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DailyBonus(Base):
    __tablename__ = "daily_bonus"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    last_claim: Mapped[date] = mapped_column(Date)
    streak: Mapped[int] = mapped_column(default=1)


class GameRound(Base):
    """Один раунд будь-якої гри. Баланс змінюється лише через леджер, ref = id раунду."""

    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    game: Mapped[str] = mapped_column(String(20))
    bet: Mapped[int] = mapped_column(BigInteger)
    payout: Mapped[int] = mapped_column(BigInteger)  # скільки повернулось гравцю (0 при програші)
    pick: Mapped[str] = mapped_column(String(16))
    outcome: Mapped[str] = mapped_column(String(16))
    request_id: Mapped[str | None] = mapped_column(String(80), unique=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
