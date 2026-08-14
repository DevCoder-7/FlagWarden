from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import api, health, webhook
from .telemetry import configure_telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FlagWarden 2.0",
    description="Security-first CTF learning and challenge management platform for Telegram",
    version="2.0.0",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(api.router)
configure_telemetry(app)

miniapp_path = Path(__file__).resolve().parent.parent / "miniapp"
if miniapp_path.exists():
    app.mount("/app", StaticFiles(directory=miniapp_path, html=True), name="miniapp")


@app.get("/")
def root():
    return {
        "name": "FlagWarden",
        "version": "2.0.0",
        "miniapp": "/app/",
        "docs": "/docs",
        "health": "/health/ready",
    }
