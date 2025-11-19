# app/crud/user.py
from typing import Optional
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User
from app.crud.base import hash_password, verify_password

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    q = select(User).where(User.email == email)
    res = await session.execute(q)
    return res.scalar_one_or_none()

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    q = select(User).where(User.id == user_id)
    res = await session.execute(q)
    return res.scalar_one_or_none()

async def create_user(session: AsyncSession, email: str, password: str, is_superuser: bool = False) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_superuser=is_superuser,
        created_at=datetime.utcnow(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def authenticate_user(session: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user