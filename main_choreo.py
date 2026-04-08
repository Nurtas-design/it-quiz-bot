import os
import logging
from fastapi import FastAPI, Request, Response, BackgroundTasks
from aiogram import Bot, Dispatcher, types
import asyncio
import uvicorn
import sys

# Папкалардан импорт ету
from config import BOT_TOKEN, ALLOWED_CHAT_IDS
import services.firebase_db as fdb
from handlers.commands import router as commands_router
from handlers.admin import router as admin_router
from handlers.quiz import router as quiz_router
from handlers.middleware import ChatFilterMiddleware
from services.question_sender import send_daily_question
from scheduler.daily_scheduler import check_and_send

# Logger орнату
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Firebase инициализациясы
fdb.init_firebase()

# Telegram Bot инициализациясы
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Middleware және Router-лерді қосу
dp.message.middleware(ChatFilterMiddleware())
dp.include_router(commands_router)
dp.include_router(admin_router)
dp.include_router(quiz_router)

# FastAPI қолданбасы
app = FastAPI(title="IT Quiz Bot", version="1.0.0")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram Webhook арқылы хабарламаларды қабылдау."""
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    """Сервердің жұмыс істеп тұрғанын тексеру."""
    return {"status": "ok", "service": "telegram-bot"}

@app.post("/scheduler")
async def trigger_scheduler(background_tasks: BackgroundTasks):
    """Choreo Scheduled Task арқылы сұрақтарды жіберу."""
    background_tasks.add_task(run_scheduler_task)
    return {"status": "scheduler triggered"}

async def run_scheduler_task():
    try:
        await check_and_send(bot)
        logger.info("Scheduler task completed.")
    except Exception as e:
        logger.error(f"Scheduler task error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
