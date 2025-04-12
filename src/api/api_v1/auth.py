import datetime
from typing import Annotated, List, Sequence

import jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from api.api_v1.auth_dependensies import get_current_user
from api.api_v1.crud.auth_crud import UserDao
from core.config import settings
from core.models import db_helper, User
from core.schemas.user import UserRead, UserCreate, UserDelete, UserAuth

router = APIRouter(
    prefix=settings.api.v1.auth,
)


@router.get("", response_model=Sequence[UserRead])
async def get_user(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    # users = await user_crud.get_all_users(session=session)
    users = await UserDao.find_all(session=session)
    return users


@router.delete("/")
async def del_user(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        user_id: UserDelete,
):
    await UserDao.del_one(session=session, id=user_id.id)
    return {"message": "пользователь удален"}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.access_token.secret_key, settings.access_token.algorithm
    )
    return encoded_jwt


async def authenticate_user(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        email: EmailStr,
        password: str,
):
    user = await UserDao.find_one_or_none(session=session, email=email)
    if not user or not verify_password(password, user.password):
        return None
    return user


@router.post("/register")
async def register_user(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        user_create: UserCreate,
):
    existing_user = await UserDao.find_one_or_none(
        session=session, email=user_create.email
    )
    if existing_user:
        raise HTTPException(status_code=500, detail="Такой пользователь уже есть!")
    hashed_password = get_hashed_password(user_create.password)
    await UserDao.register_add(
        session=session,
        username=user_create.username,
        email=user_create.email,
        password=hashed_password,
    )
    return {"message": "success"}


@router.post("/login")
async def login_user(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        user_auth: UserAuth,
        response: Response,
):
    user = await authenticate_user(
        session=session, email=user_auth.email, password=user_auth.password
    )
    if not user:
        raise HTTPException(status_code=401)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("user_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.get("/current")
async def get_choto(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("user_access_token")
    return {"message": "User logout"}
