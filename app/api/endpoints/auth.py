import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api import deps
from app.core import config, security
from app.models.model import User
from app.schemas.requests import RefreshTokenRequest
from app.schemas.responses import AccessTokenResponse

router = APIRouter()


@router.post("/access-token", response_model=AccessTokenResponse)
async def login_access_token(
    session: AsyncSession = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """OAuth2 compatible token, get an access token for future requests using username and password"""

    result = await session.exec(select(User).where(User.username == form_data.username))
    user: User = result.one_or_none()

    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.verified:
        raise HTTPException(status_code=400, detail="User has not been verified")

    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return security.generate_access_token_response(
        str(user.id), role=user.role, username=user.username
    )


@router.post("/refresh-token", response_model=AccessTokenResponse)
async def refresh_token(
    input: RefreshTokenRequest,
    session: AsyncSession = Depends(deps.get_session),
):
    """OAuth2 compatible token, get an access token for future requests using refresh token"""
    try:
        payload = jwt.decode(
            input.refresh_token,
            config.settings.SECRET_KEY,
            algorithms=[security.JWT_ALGORITHM],
        )
    except (jwt.DecodeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, unknown error",
        )

    # JWT guarantees payload will be unchanged (and thus valid), no errors here
    token_data = security.JWTTokenPayload(**payload)

    if not token_data.refresh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, cannot use access token",
        )
    now = int(time.time())
    if now < token_data.issued_at or now > token_data.expires_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, token expired or not yet valid",
        )

    result = await session.exec(select(User).where(User.id == token_data.sub))
    user: User | None = result.one()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return security.generate_access_token_response(
        str(user.username), role=user.role, username=user.username
    )
