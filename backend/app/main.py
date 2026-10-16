from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import auth, games, wallet


@asynccontextmanager
async def lifespan(_: FastAPI):
    # На старті таблиці створюються автоматично. Далі переходимо на Alembic-міграції.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Casino API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(wallet.router)
api.include_router(games.router)


@api.get("/health")
async def health():
    return {"ok": True}


app.include_router(api)
