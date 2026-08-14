from dataclasses import dataclass
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import Role, User
from .security import AuthenticationError, verify_telegram_init_data
from .users import ROLE_RANK, get_or_create_user


@dataclass
class AuthContext:
    user: User


def current_user(
    x_telegram_init_data: str | None = Header(default=None),
    x_debug_telegram_id: int | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    settings = get_settings()
    if settings.environment == "development" and settings.allow_debug_auth and x_debug_telegram_id:
        user = get_or_create_user(db, x_debug_telegram_id, username="debug-user")
        db.commit()
        return user
    try:
        identity = verify_telegram_init_data(
            x_telegram_init_data or "",
            settings.telegram_bot_token,
            settings.miniapp_auth_max_age_seconds,
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_or_create_user(db, identity.user_id, identity.username)
    db.commit()
    return user


def require_role(min_role: Role):
    def dependency(user: User = Depends(current_user)) -> User:
        if ROLE_RANK.get(user.role, 0) < ROLE_RANK[min_role.value]:
            raise HTTPException(status_code=403, detail=f"Requires role {min_role.value} or higher")
        return user
    return dependency
