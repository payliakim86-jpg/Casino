import secrets

from ..config import settings


def flip() -> str:
    return "heads" if secrets.randbelow(2) == 0 else "tails"


def payout(bet: int) -> int:
    return bet * settings.coinflip_payout_bp // 10_000
