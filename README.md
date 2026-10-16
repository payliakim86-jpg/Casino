# Casino (віртуальні монети)

## Запуск
Бекенд (за замовчуванням SQLite, нічого більше не треба):
    cd backend
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload
    pytest            # smoke-тест: реєстрація, бонус, леджер

Фронтенд (в іншому терміналі):
    cd frontend
    npm install
    npm run dev       # http://localhost:5173, /api проксується на :8000

Postgres замість SQLite: `docker compose up -d`, потім у backend/.env
DATABASE_URL=postgresql+asyncpg://casino:casino@localhost:5432/casino

## Структура
- backend/app/services/wallet.py: єдине місце, де змінюється баланс (леджер, ідемпотентність, блокування рядка)
- backend/app/routers/: auth (нік + пароль), wallet (/me, бонус, леджер)
- frontend/: React + Vite + PWA (manifest і service worker вже налаштовані)

## Далі
Ігри лежать у backend/app/games/ (логіка) і backend/app/routers/games.py (ендпоінти). Готово: монетка. Кожен раунд пишеться в game_rounds, баланс змінюється тільки через wallet.apply().
Перед продакшеном: Alembic замість create_all, довгий SECRET_KEY, HTTPS, обмеження частоти запитів.
