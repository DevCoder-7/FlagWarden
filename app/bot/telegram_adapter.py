from __future__ import annotations

import logging
from typing import Any

from app.bot.flow import BotFlow, BotResponse

logger = logging.getLogger(__name__)


class TelegramAdapter:
    """Telegram Bot API adapter.

    Imports from python-telegram-bot are intentionally lazy so local tests and health
    checks can run without a bot token or network access.
    """

    def __init__(self, flow: BotFlow, token: str | None = None) -> None:
        self.flow = flow
        self.token = token
        self._application: Any | None = None
        self._initialized = False

    async def handle_text(
        self,
        user_id: str,
        text: str,
        display_name: str | None = None,
    ) -> BotResponse:
        return self.flow.handle_text("telegram", str(user_id), text, display_name)

    def build_application(self) -> Any:
        if not self.token:
            raise RuntimeError("Telegram bot token is not configured")
        if self._application is not None:
            return self._application

        from telegram.ext import (
            Application,
            CallbackQueryHandler,
            CommandHandler,
            MessageHandler,
            filters,
        )

        application = Application.builder().token(self.token).build()
        command_names = [
            "start",
            "help",
            "categories",
            "daily",
            "quiz",
            "challenge",
            "hint",
            "answer",
            "score",
            "leaderboard",
            "profile",
            "report",
            "safety",
        ]
        application.add_handler(CommandHandler(command_names, self._on_message))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message))
        application.add_handler(CallbackQueryHandler(self._on_callback))
        self._application = application
        return application

    async def process_update_json(self, update_json: dict[str, Any]) -> None:
        from telegram import Update

        application = self.build_application()
        if not self._initialized:
            await application.initialize()
            self._initialized = True

        update = Update.de_json(update_json, application.bot)
        await application.process_update(update)

    async def _on_message(self, update: Any, context: Any) -> None:
        del context
        message = update.effective_message
        user = update.effective_user
        if not message or not user or not getattr(message, "text", None):
            return

        display_name = getattr(user, "full_name", None) or getattr(user, "username", None)
        response = await self.handle_text(str(user.id), message.text, display_name)
        await self._reply(message, response)

    async def _on_callback(self, update: Any, context: Any) -> None:
        del context
        query = update.callback_query
        if not query:
            return
        await query.answer()
        user = query.from_user
        display_name = getattr(user, "full_name", None) or getattr(user, "username", None)
        response = await self.handle_text(str(user.id), query.data or "/help", display_name)
        await self._reply(query.message, response)

    async def _reply(self, message: Any, response: BotResponse) -> None:
        reply_markup = self._build_markup(response)
        await message.reply_text(response.text, reply_markup=reply_markup)

    def _build_markup(self, response: BotResponse) -> Any | None:
        if not response.buttons:
            return None

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        rows = [
            [InlineKeyboardButton(button.label, callback_data=button.command)]
            for button in response.buttons
        ]
        return InlineKeyboardMarkup(rows)

