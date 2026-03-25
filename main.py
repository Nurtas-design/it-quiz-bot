"""
main.py — IT Quiz Bot негізгі файлы
Telegram бот іске қосу, роутерлерді тіркеу, scheduler іске қосу.

Іске қосу:
  python main.py
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Модульдер
import config
import firebase_db as fdb
from handlers.middleware import ChatFilterMiddleware
from handlers import commands, admin, quiz
from scheduler.daily_scheduler import start_scheduler

# ===== Логирование =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Бот іске қосылғанда."""
    logger.info("=" * 50)
    logger.info("🤖 IT Quiz Bot іске қосылуда...")
    logger.info(f"   Админдер: {config.ADMIN_IDS}")
    logger.info(f"   Чаттар: {config.ALLOWED_CHAT_IDS}")
    logger.info(f"   Уақыт белдеуі: {config.TIMEZONE}")
    logger.info(f"   Сұрақ уақыттары: {config.QUESTION_HOURS}")
    logger.info("=" * 50)

    # Scheduler іске қосу
    await start_scheduler(bot)

    # Админдерге хабар жіберу
    unused = fdb.get_unused_count()
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🤖 <b>IT Quiz Bot іске қосылды!</b>\n\n"
                f"📊 Пайдаланылмаған сұрақтар: <b>{unused}</b>\n"
                f"⏰ Сұрақ уақыттары: {config.QUESTION_HOURS}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Админге хабар жіберу қатесі ({admin_id}): {e}")


async def main():
    """Негізгі функция."""

    # Firebase инициализация
    fdb.init_firebase()

    # Bot & Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Middleware тіркеу
    dp.message.middleware(ChatFilterMiddleware())

    # Роутерлерді тіркеу
    dp.include_router(admin.router)     # Админ командалары — бірінші
    dp.include_router(commands.router)  # Қолданушы командалары
    dp.include_router(quiz.router)      # Сұрақ жауаптары

    # Startup callback
    dp.startup.register(on_startup)

    # Polling іске қосу
    logger.info("🚀 Polling іске қосылуда...")
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()
        logger.info("🛑 Бот тоқтатылды")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот тоқтатылды (Ctrl+C)")
    except Exception as e:
        logger.critical(f"💥 Критикалық қате: {e}", exc_info=True)
        sys.exit(1)