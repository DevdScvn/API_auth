from datetime import datetime
from typing import Annotated

from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from starlette.requests import Request

from api.api_v1.crud.auth_crud import UserDao
from core.config import settings
from core.models import db_helper


def get_token(request: Request):
    token = request.cookies.get("user_access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current_user(session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
                           token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.access_token.secret_key, settings.access_token.algorithm
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    expire: str = payload.get("exp")
    if not expire or int(expire) < datetime.utcnow().timestamp():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await UserDao.find_one_or_none(session=session, id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
