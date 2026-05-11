from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import COOKIE_NAME, current_user
from app.auth.jwt import issue_token
from app.auth.passwords import hash_password, verify_password
from app.auth.schemas import LoginRequest, RegisterRequest, UserResponse
from app.core.config import settings
from app.core.database import get_session
from app.models.db.user import User

router = APIRouter()


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.JWT_LIFETIME_SECONDS,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        is_active=True,
        is_verified=False,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    await session.refresh(user)

    _set_auth_cookie(response, issue_token(user.id))
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    body: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive"
        )

    _set_auth_cookie(response, issue_token(user.id))
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return None


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(current_user)):
    return user
