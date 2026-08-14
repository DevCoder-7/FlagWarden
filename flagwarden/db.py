from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    url = get_settings().database_url
    kwargs = {"future": True, "pool_pre_ping": True}
    if url == "sqlite:///:memory:":
        kwargs.update({"connect_args": {"check_same_thread": False}, "poolclass": StaticPool})
    elif url.startswith("sqlite"):
        kwargs.update({"connect_args": {"check_same_thread": False}})
    return create_engine(url, **kwargs)


@lru_cache
def get_session_factory():
    return sessionmaker(bind=get_engine(), class_=Session, expire_on_commit=False)


def get_db():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from . import models  # noqa: F401
    Base.metadata.create_all(get_engine())


def reset_db_caches() -> None:
    get_session_factory.cache_clear()
    get_engine.cache_clear()
