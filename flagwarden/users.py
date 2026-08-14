from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .models import Role, User

ROLE_RANK = {Role.USER.value: 0, Role.AUTHOR.value: 1, Role.REVIEWER.value: 2, Role.ADMIN.value: 3}


def configured_role(telegram_user_id: int) -> str:
    s = get_settings()
    if telegram_user_id in s.admin_ids:
        return Role.ADMIN.value
    if telegram_user_id in s.reviewer_ids:
        return Role.REVIEWER.value
    if telegram_user_id in s.author_ids:
        return Role.AUTHOR.value
    return Role.USER.value


def get_or_create_user(db: Session, telegram_user_id: int, username: str | None = None) -> User:
    user = db.scalar(select(User).where(User.telegram_user_id == telegram_user_id))
    role = configured_role(telegram_user_id)
    if user is None:
        user = User(telegram_user_id=telegram_user_id, username=username, role=role)
        db.add(user)
        db.flush()
    else:
        if username and username != user.username:
            user.username = username
        # Explicit DB promotions are preserved unless config grants a higher role.
        if ROLE_RANK[role] > ROLE_RANK.get(user.role, 0):
            user.role = role
    return user
