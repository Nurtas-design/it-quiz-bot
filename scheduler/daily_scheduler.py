"""
scheduler/daily_scheduler.py — Күн сайын сұрақ жіберу scheduler
Random уақыт таңдау логикасы:

1. Күн сайын 00:05-те RANDOM уақыт таңдалады (09:00, 12:00, 15:00, 18:00, 21:00)
2. Таңдалған уақытта сұрақ жіберіледі
3. Бір күнде тек 1 сұрақ
4. Бір рет жіберілсе — қайта жіберілмейді

Жұмыс логикасы:
- Әр минутта тексеріледі (check_and_send)
- Бүгін сұрақ жіберілді ме? → жоқ болса жіберу уақытын тексеру
- Уақыт келді ме? → сұрақ жіберу
"""

import asyncio
import random
import logging
from datetime import datetime, date, time

import pytz

import config
import firebase_db as fdb
from services.question_sender import send_daily_question

logger = logging.getLogger(__name__)


def get_local_now() -> datetime:
    """Жергілікті уақытты алу."""
    tz = pytz.timezone(config.TIMEZONE)
    return datetime.now(tz)


def select_random_hour() -> int:
    """Рандом уақыт таңдау."""
    return random.choice(config.QUESTION_HOURS)


async def check_and_send(bot):
    """
    Тексеру және жіберу логикасы.
    Әр минутта шақырылады.
    """
    now = get_local_now()
    today_str = date.today().isoformat()
    current_hour = now.hour
    current_minute = now.minute

    # Бүгін жіберілді ме?
    daily = fdb.get_daily_question(today_str)
    if daily:
        # Бүгін бұрын жіберілген — ештеңе істемеу
        return

    # Scheduler state тексеру
    state = fdb.get_scheduler_state()

    if not state or state.get("last_question_date") != today_str:
        # Жаңа күн — рандом уақыт таңдау
        selected_hour = select_random_hour()
        fdb.set_scheduler_state(today_str, selected_hour)
        logger.info(f"🎲 Бүгінгі сұрақ уақыты: {selected_hour}:00")
    else:
        selected_hour = state.get("selected_hour", 12)

    # Уақыт келді ме? (таңдалған сағат, 0-4 минут аралығында)
    if current_hour == selected_hour and current_minute < 5:
        logger.info(f"⏰ Сұрақ жіберу уақыты келді: {current_hour}:{current_minute:02d}")
        success = await send_daily_question(bot)
        if success:
            logger.info("✅ Бүгінгі сұрақ сәтті жіберілді")
        else:
            logger.warning("⚠️ Сұрақ жіберілмеді")


async def scheduler_loop(bot):
    """
    Негізгі scheduler цикл.
    Әр 60 секундта check_and_send шақырады.
    """
    logger.info("🚀 Scheduler іске қосылды")

    while True:
        try:
            await check_and_send(bot)
        except Exception as e:
            logger.error(f"❌ Scheduler қатесі: {e}", exc_info=True)

        # 60 секунд күту
        await asyncio.sleep(60)


async def start_scheduler(bot):
    """Scheduler-ді background task ретінде іске қосу."""
    asyncio.create_task(scheduler_loop(bot))
    logger.info("✅ Scheduler background task іске қосылды")