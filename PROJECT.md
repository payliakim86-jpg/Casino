# Casino (віртуальні монети): контекст проєкту

Сайт-казино на віртуальній валюті, без реальних грошей. Працює як PWA, пізніше можна обгорнути (Capacitor, TWA) або відкрити як Telegram Mini App.

## Стек
- Бекенд: Python, FastAPI, SQLAlchemy async, SQLite (dev) / PostgreSQL (prod), JWT, bcrypt
- Фронтенд: React + Vite + TypeScript, vite-plugin-pwa
- Тести: pytest (backend/tests)

## Структура
- `backend/app/services/wallet.py`: єдине місце, де змінюється баланс
- `backend/app/routers/`: auth, wallet (/me, бонус, леджер), games
- `backend/app/games/`: чиста логіка ігор (RNG, виплати)
- `backend/app/models.py`: users, wallets, ledger, daily_bonus, game_rounds
- `frontend/src/`: App.tsx (лобі), CoinFlip.tsx, api.ts, styles.css

## Правила (не порушувати)
1. Баланс змінюється тільки через `wallet.apply()`. Кожна зміна це запис у `ledger`, записи не редагуються.
2. Вся логіка ігор і RNG тільки на сервері (`secrets`). Клієнт лише показує результат.
3. Кожна гра: перевірка ліміту ставки, `lock_wallet` на початку, запис у `game_rounds`, `request_id` для захисту від дублів.
4. Нова гра = новий модуль у `app/games/` + ендпоінт у `routers/games.py` + тест + екран у фронтенді.
5. Нові таблиці/колонки: після переходу на Alembic тільки через міграції.
6. Тексти інтерфейсу українською. Валюта віртуальна: без кнопок поповнення та виведення.

## Економіка (backend/app/config.py)
Старт 100 монет. Щоденний бонус 50 + 10 за день серії, максимум 110 (7 днів). Ставка 10–1000. Монетка платить ×1.95.

## Дизайн: Gold & Graphite
Графітовий фон (#131315), золоті акценти (#e3b84f, #f2d27a), слонова кістка для тексту, серифні заголовки (Cormorant Garamond), текст Manrope. Усі кольори це CSS-змінні в `frontend/src/styles.css`.

## Запуск і перевірка
Дивись README.md. Перед комітом: `pytest` у `backend/` і `npm run build` у `frontend/`.

## Статус
Готово: реєстрація за ніком, гаманець і леджер, щоденний бонус, Монетка, PWA, тема.
Далі (кандидати): лідерборд, слоти, provably fair, Alembic, обмеження частоти запитів, деплой.
