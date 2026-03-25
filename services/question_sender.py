"""
services/question_sender.py — Сұрақ жіберу сервисі
"""

import logging
import random
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import firebase_db as fdb

logger = logging.getLogger(__name__)


async def send_daily_question(bot: Bot) -> bool:
    today = fdb.get_today_str()

    daily = fdb.get_daily_question(today)
    if daily:
        return False

    result = fdb.get_unused_question()
    if not result:
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    "<b>⚠️ Сұрақтар таусылды!</b>\n"
                    "/addquestion командасымен жаңа сұрақ қосыңыз.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        return False

    question_id, question = result

    options = list(question["options"])
    correct_index = question["correct_answer"]
    correct_text = options[correct_index]

    shuffled = list(range(4))
    random.shuffle(shuffled)

    shuffled_options = [options[i] for i in shuffled]
    new_correct_index = shuffled_options.index(correct_text)

    letters = ["A", "B", "C", "D"]

    text = (
        "🧠 <b>IT Quiz — Бүгінгі сұрақ!</b>\n\n"
        f"📂 Категория: <i>{question.get('category', 'IT')}</i>\n\n"
        f"❓ {question['text']}\n\n"
    )
    for i, opt in enumerate(shuffled_options):
        text += f"  {letters[i]}) {opt}\n"

    text += "\n⬇️ Жауап беру үшін батырманы басыңыз:"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="A", callback_data="answer_0"),
            InlineKeyboardButton(text="B", callback_data="answer_1"),
        ],
        [
            InlineKeyboardButton(text="C", callback_data="answer_2"),
            InlineKeyboardButton(text="D", callback_data="answer_3"),
        ]
    ])

    sent = False
    for chat_id in config.ALLOWED_CHAT_IDS:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            sent = True
        except Exception as e:
            logger.error(f"Сұрақ жіберу қатесі (chat={chat_id}): {e}")

    if sent:
        fdb.mark_question_used(question_id)
        fdb.set_daily_question_with_shuffle(
            today, question_id, shuffled_options, new_correct_index
        )

    return sent