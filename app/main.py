from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.bot.flow import BotFlow
from app.bot.telegram_adapter import TelegramAdapter
from app.bot.whatsapp_adapter import WhatsAppAdapter
from app.config import Settings, get_settings
from app.core.content import ChallengeBank
from app.core.safety import SafetyChecker
from app.db.repository import build_engine, build_session_factory, init_db


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                continue
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    content_path = Path(settings.challenge_data_path)
    challenge_bank = ChallengeBank.from_file(content_path)
    engine = build_engine(settings.database_url)
    session_factory = build_session_factory(engine)

    safety_checker = SafetyChecker()
    flow = BotFlow(challenge_bank, session_factory, settings, safety_checker=safety_checker)
    telegram = TelegramAdapter(flow, token=settings.secret_value(settings.telegram_bot_token))
    whatsapp = WhatsAppAdapter(settings, flow)

    logger.info("app_config_loaded", extra={"settings": settings.redacted_dict()})
    if not settings.telegram_enabled:
        logger.info("telegram_integration_disabled")
    if not settings.whatsapp_enabled:
        logger.info(
            "whatsapp_integration_disabled",
            extra={"missing": settings.missing_whatsapp_vars()},
        )
    if not settings.llm_enabled:
        logger.info("llm_integration_disabled")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("database_initializing")
        init_db(engine)
        logger.info("database_ready")
        yield

    app = FastAPI(
        title=f"{settings.app_name} API",
        description=(
            "Webhook backend for FlagWarden, a Telegram CTF Cybersecurity Learning Bot."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.challenge_bank = challenge_bank
    app.state.flow = flow
    app.state.telegram = telegram
    app.state.whatsapp = whatsapp

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "app": settings.app_name,
            "environment": settings.app_env,
            "telegram_enabled": settings.telegram_enabled,
            "whatsapp_enabled": settings.whatsapp_enabled,
            "llm_enabled": settings.llm_enabled,
            "challenge_count": len(challenge_bank.all()),
        }

    @app.get("/metrics")
    def metrics() -> dict[str, Any]:
        return {"bot": flow.metrics.snapshot()}

    @app.post("/telegram/webhook")
    async def telegram_webhook(request: Request) -> dict[str, bool]:
        if not settings.telegram_enabled:
            raise HTTPException(status_code=503, detail="Telegram integration is disabled")
        payload = await request.json()
        await telegram.process_update_json(payload)
        return {"ok": True}

    @app.get("/webhooks/whatsapp")
    async def whatsapp_verify(
        hub_mode: str | None = Query(default=None, alias="hub.mode"),
        hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
        hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
    ) -> PlainTextResponse:
        challenge = whatsapp.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
        return PlainTextResponse(challenge)

    @app.post("/webhooks/whatsapp")
    async def whatsapp_webhook(payload: dict[str, Any]) -> dict[str, Any]:
        return await whatsapp.handle_webhook(payload)

    return app


app = create_app()
