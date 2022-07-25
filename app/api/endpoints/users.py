from http.client import HTTPResponse
import json
import uuid
import random
import string
from datetime import datetime
from typing import List


import pytz
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.model import Role
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.model import Device, User
from app.schemas.requests import (
    UserCreateRequest,
    UserForgotPasswordRequest,
    UserUpdatePasswordRequest,
    UserUpdateProfileRequest,
)
from app.schemas.responses import BaseUserResponse, UserConfirmationResponse, UserDeviceInResponse, UserResponse
from app.core.utils import generate_random_password, send_new_account_email, send_reset_password_email
from app.core.utils import generate_confirmation_token, confirm_token
from fastapi.responses import HTMLResponse

router = APIRouter()
timezone = pytz.timezone(settings.TIMEZONE)


@router.get("/me", response_model=UserDeviceInResponse)
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Get current user"""
    try:
        result = await session.exec(
            select(Device).where(Device.user_id == current_user.id)
        )
        devices = result.fetchall()
        response = UserDeviceInResponse(
            id=current_user.id,
            username=current_user.username,
            nik=current_user.nik,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            address=current_user.address,
            phone_no=current_user.phone_no,
            role=current_user.role,
            verified=current_user.verified,
            devices=devices,
        )
        return response
    except Exception as ex:
        print(str(ex))
        raise HTTPException(
            status_code=500, detail="Something went wrong. Contact your admin"
        )


@router.patch("/me/profile", response_model=UserResponse)
async def update_profile(
    user_request: UserUpdateProfileRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Update current user profile"""
    print(user_request)
    try:
        for k, v in user_request.dict(exclude_unset=True).items():
            setattr(current_user, k, v)
        setattr(current_user, "modified_at", datetime.now(timezone))
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        return current_user
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Something went wrong. rollback has occured"
        )


@router.get("/{id}", response_model=UserDeviceInResponse)
async def get_user_by_id(
    id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Get user detail by id"""
    if current_user.role is not Role.admin:
        raise HTTPException(
            status_code=401, detail="Not permissible for this role")
    result = await session.exec(select(User).where(User.id == id))
    user = result.one_or_none()
    if user is None:
        raise HTTPException(
            status_code=400, detail=f"User with id {id} not found")
    try:
        result = await session.exec(select(Device).where(Device.user_id == id))
        devices = result.fetchall()
        response = UserDeviceInResponse(
            id=user.id,
            username=user.username,
            nik=user.nik,
            first_name=user.first_name,
            last_name=user.last_name,
            address=user.address,
            phone_no=user.phone_no,
            role=user.role,
            devices=devices,
        )
        return response
    except Exception as ex:
        print(str(ex))
        raise HTTPException(
            status_code=500, detail="Something went wrong. Contact your admin"
        )


@router.delete("/{id}")
async def delete_user_by_id(
    id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Delete user by id
    Prerequisites:
    1. User does not have device assigned
    """
    if current_user.role is not Role.admin:
        raise HTTPException(
            status_code=401, detail="Not permissible for this role")

    # check whether user has devices assigned
    result = await session.exec(select(User).where(User.id == id))
    user = result.one_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail=f"No user with {id}")
    if hasattr(user, "devices"):
        raise HTTPException(
            status_code=400, detail=f"User {id} has devices. can not be deleted. "
        )
    try:
        await session.exec(delete(User).where(User.id == id))
        await session.commit()
        return {"ok": True, "message": f"Delete {id} was successful"}
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Something went wrong. rollback has occured"
        )


@router.post("/me/reset-password", response_model=BaseUserResponse)
async def reset_current_user_password(
    user_update_password: UserUpdatePasswordRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """Update current user password"""
    try:
        current_user.hashed_password = get_password_hash(
            user_update_password.password)
        current_user.modified_at = datetime.now(timezone)
        session.add(current_user)
        await session.commit()
        return current_user
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Something went wrong. rollback has occured"
        )


@router.post("/forgot-password", response_model=BaseUserResponse)
async def forgot_password(
    user: UserForgotPasswordRequest,
    session: AsyncSession = Depends(deps.get_session),
):
    """Create new password in case user forgot his/her password"""
    
    result = await session.exec(select(User).where(User.username == user.username))
    user = result.one_or_none()
    if user is None:
        raise HTTPException(status_code=400,detail='User is not registered')
    try:
        new_password = generate_random_password(length=12)
        hashed_password = get_password_hash(new_password)
        setattr(user, 'hashed_password', hashed_password)
        session.add(user)
        await session.commit()
        if settings.EMAILS_ENABLED:
            task = BackgroundTasks()
            task.add_task(
                send_reset_password_email(
                    user.username, new_password=new_password)
            )
        return user
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Something went wrong. rollback has occured"
        )


@router.post("/register", response_model=BaseUserResponse)
async def register_new_user(
    new_user: UserCreateRequest,
    # current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Create new user"""
    # if current_user.role is not Role.admin:
    #     raise HTTPException(status_code=401, detail="Not permissible for this role")

    result = await session.exec(select(User).where(User.username == new_user.username))
    user = result.one_or_none()
    chars = string.digits
    if user is not None:
        raise HTTPException(
            status_code=400, detail="Cannot use this email address")
    try:
        user = User(
            username=new_user.username,
            # "".join(random.choice(chars) for i in range(16)),
            nik=new_user.nik,
            hashed_password=get_password_hash(new_user.password),
            role=Role.merchant,  # new_user.role,
            phone_no=new_user.phone_no,
            verified=False,
            created_at=datetime.now(timezone),
            modified_at=datetime.now(timezone),
        )
        session.add(user)
        await session.commit()
        token = generate_confirmation_token(user.username)
        link = f'https://raspi-geek.tech/api/v1/users/confirm/{token}'
        print(token)
        if settings.EMAILS_ENABLED:
            task = BackgroundTasks()
            task.add_task(
                send_new_account_email(
                    email_to=new_user.username,
                    username=new_user.username,
                    password='',
                    link=link
                )
            )
        return user
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=json.dumps(str(e)))


@router.get('/confirm/{token}', response_class=HTMLResponse, include_in_schema=False)
async def email_confirmation(
    token: str,
    session: AsyncSession = Depends(deps.get_session),
):
    """Email confirmation to verify user"""
    try:
        email = confirm_token(token)
        result = await session.exec(select(User).where(User.username == email))
        user = result.one_or_none()
        setattr(user, 'verified', True)
        session.add(user)
        await session.commit()
        with open('/app/app/static/welcome.html') as f:
            data=f.read()
        return HTMLResponse(content=data)
    except Exception:
        return """
        <html>
            <head>
                <title>Email Confirmation Failed</title>
            </head>
            <body>
                <h3>Email tidak berhasil dikonfirmasi!</h3>
                <p>Silakan cek kembali alamat email anda</p>
            </body>
        </html>
        """


@router.get("/", response_model=List[BaseUserResponse])
async def get_user_list(
    # current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Get user list"""
    result = await session.exec(select(User))
    users = result.all()
    return users
