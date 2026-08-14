import os
import pytest
from fastapi.testclient import TestClient

os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TELEGRAM_BOT_TOKEN"] = "123456:test-token"
os.environ["TELEGRAM_WEBHOOK_SECRET"] = "test-webhook-secret"
os.environ["ANSWER_PEPPER"] = "development-only-change-me"
os.environ["ALLOW_DEBUG_AUTH"] = "true"
os.environ["ADMIN_TELEGRAM_IDS"] = "10001"
os.environ["REVIEWER_TELEGRAM_IDS"] = "10002"
os.environ["AUTHOR_TELEGRAM_IDS"] = "10003"

from flagwarden.config import get_settings
from flagwarden.db import Base, get_engine, init_db
from flagwarden.main import app


@pytest.fixture(autouse=True)
def clean_db():
    get_settings.cache_clear()
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
