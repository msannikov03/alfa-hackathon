from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import User
from app.api.auth import get_current_user_optional

router = APIRouter()


class NotificationSettings(BaseModel):
    enabled: bool = True
    email: bool = True
    telegram: bool = True


class PreferenceSettings(BaseModel):
    language: str = "ru"
    timezone: str = "Europe/Moscow"
    currency: str = "RUB"


class SettingsResponse(BaseModel):
    user_id: int
    notifications: NotificationSettings
    preferences: PreferenceSettings


class SettingsUpdate(BaseModel):
    notifications: Optional[NotificationSettings] = None
    preferences: Optional[PreferenceSettings] = None


async def _get_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _build_response(user: User) -> SettingsResponse:
    settings_blob = (user.business_data or {}).get("settings", {})

    notifications_data = settings_blob.get("notifications", {})
    preferences_data = settings_blob.get("preferences", {})

    notifications = NotificationSettings(
        **{**NotificationSettings().model_dump(), **notifications_data}
    )
    preferences = PreferenceSettings(
        **{**PreferenceSettings().model_dump(), **preferences_data}
    )

    return SettingsResponse(
        user_id=user.id,
        notifications=notifications,
        preferences=preferences,
    )


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Return notification and localization preferences for the user."""
    user = await _get_user(db, user_id)
    return _build_response(user)


@router.post("/", response_model=SettingsResponse)
async def update_settings(
    payload: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Upsert user settings and persist them inside business_data."""
    user = await _get_user(db, user_id)
    business_data = user.business_data or {}
    settings_blob = business_data.get("settings", {})

    if payload.notifications is not None:
        settings_blob["notifications"] = payload.notifications.model_dump()
    else:
        settings_blob.setdefault("notifications", NotificationSettings().model_dump())

    if payload.preferences is not None:
        settings_blob["preferences"] = payload.preferences.model_dump()
    else:
        settings_blob.setdefault("preferences", PreferenceSettings().model_dump())

    business_data["settings"] = settings_blob
    user.business_data = business_data

    await db.commit()
    await db.refresh(user)

    return _build_response(user)
