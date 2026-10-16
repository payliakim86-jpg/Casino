from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .models import User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


async def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    user_id = decode_token(creds.credentials) if creds else None
    user = await session.get(User, user_id) if user_id else None
    if not user:
        raise HTTPException(401, "Потрібно увійти")
    return user
