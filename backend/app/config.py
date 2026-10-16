from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./casino.db"
    secret_key: str = "change-me"
    token_ttl_minutes: int = 60 * 24 * 7

    # Економіка
    start_balance: int = 100
    bonus_base: int = 50
    bonus_step: int = 10
    bonus_max_streak: int = 7

    # Ставки
    min_bet: int = 10
    max_bet: int = 1000
    coinflip_payout_bp: int = 19500  # виплата ×1.95 (в базисних пунктах), різниця з ×2 це «комісія»


settings = Settings()
