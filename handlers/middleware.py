"""
handlers/middleware.py — Қауіпсіздік middleware
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

import config

logger = logging.getLogger(__name__)

ADMIN_ONLY_COMMANDS = {"/addquestion", "/skip", "/questioncount", "/test", "/delquestion", "/listquestions"}


class ChatFilterMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        message: Message = event
        chat_id = message.chat.id
        chat_type = message.chat.type

        if chat_type == "private":
            return await handler(event, data)

        if chat_id not in config.ALLOWED_CHAT_IDS:
            return

        if message.text:
            cmd = message.text.split()[0].split("@")[0].lower()
            if cmd in ADMIN_ONLY_COMMANDS:
                try:
                    await message.delete()
                except Exception as e:
                    logger.warning(f"Хабарды өшіру қатесі: {e}")
                return

        return await handler(event, data)