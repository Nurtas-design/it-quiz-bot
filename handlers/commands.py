"""
handlers/commands.py — Қолданушы командалары
"""

import logging
from datetime import date
from aiogram import Router, types
from aiogram.filters import Command

import config
import firebase_db as fdb

logger = logging.getLogger(__name__)
router = Router()


def is_allowed_chat(chat_id: int) -> bool:
    return chat_id in config.ALLOWED_CHAT_IDS


def is_private(message: types.Message) -> bool:
    return message.chat.type == "private"


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if not is_private(message):
        return

    user = message.from_user
    if user:
        fdb.save_user(user.id, user.username, user.first_name)

    name = user.first_name if user else "Қолданушы"
    await message.answer(
        f"👋 Сәлем, {name}!\n\n"
        "Мен IT Quiz Bot-пын — IT білімін тексеретін бот.\n"
        "Топта күн сайын сұрақ жіберемін.\n\n"
        "📋 Командалар:\n"
        "/help — Барлық командалар\n"
        "/top — Рейтинг\n"
        "/stats — Менің статистикам\n"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    chat_id = message.chat.id
    if not is_private(message) and not is_allowed_chat(chat_id):
        return

    text = (
        "📚 <b>IT Quiz Bot — Командалар</b>\n\n"
        "👥 <b>Топ командалары:</b>\n"
        "/top — Рейтинг (күндік/айлық/жылдық)\n"
        "/stats — Менің статистикам\n"
        "/help — Осы мәзір\n\n"
        "🔒 <b>Админ командалары (PM):</b>\n"
        "/addquestion — Сұрақ қосу\n"
        "/delquestion — Сұрақ өшіру\n"
        "/listquestions — Сұрақтар тізімі\n"
        "/test — Тест сұрақ жіберу\n"
        "/skip — Бүгінгі сұрақты өткізу\n"
        "/questioncount — Сұрақтар саны\n"
        "/cancel — Процессті тоқтату\n"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("top"))
async def cmd_top(message: types.Message):
    chat_id = message.chat.id
    if not is_private(message) and not is_allowed_chat(chat_id):
        return

    today = date.today()
    today_str = today.isoformat()
    month_str = today_str[:7]
    year_str = today_str[:4]

    daily_top = fdb.get_top_users("daily", today_str, limit=10)
    monthly_top = fdb.get_top_users("monthly", month_str, limit=10)
    yearly_top = fdb.get_top_users("yearly", year_str, limit=10)

    text = "🏆 <b>РЕЙТИНГ</b>\n\n"

    text += f"📅 <b>Бүгін ({today_str}):</b>\n"
    text += _format_top_list(daily_top)

    text += f"\n📆 <b>Ай ({month_str}):</b>\n"
    text += _format_top_list(monthly_top)

    text += f"\n📊 <b>Жыл ({year_str}):</b>\n"
    text += _format_top_list(yearly_top)

    await message.answer(text, parse_mode="HTML")


def _format_top_list(top_list: list[tuple[int, int]]) -> str:
    if not top_list:
        return "  — Әлі деректер жоқ\n"

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (user_id, points) in enumerate(top_list):
        user = fdb.get_user(user_id)
        name = "Белгісіз"
        if user:
            name = user.get("username") or user.get("first_name") or "Белгісіз"
            if user.get("username"):
                name = f"@{name}"

        prefix = medals[i] if i < 3 else f"  {i + 1}."
        lines.append(f"{prefix} {name} — <b>{points}</b> ұпай")

    return "\n".join(lines) + "\n"


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    chat_id = message.chat.id
    if not is_private(message) and not is_allowed_chat(chat_id):
        return

    user = message.from_user
    # Анонимді хабар — sender_chat арқылы жіберілген
    if not user or user.is_bot:
        # Анонимді админ жазса — user жоқ
        await message.answer(
            "ℹ️ Анонимді режимде статистика көрсету мүмкін емес.\n"
            "Анонимді режимді өшіріп, қайта жазыңыз.",
            parse_mode="HTML"
        )
        return

    user_id = user.id
    fdb.save_user(user_id, user.username, user.first_name)

    stats = fdb.get_user_stats(user_id)
    name = stats.get("first_name") or stats.get("username") or "Қолданушы"

    text = (
        f"📊 <b>{name} — Статистика</b>\n\n"
        f"📅 Бүгін: <b>{stats['daily']}</b> ұпай\n"
        f"📆 Ай: <b>{stats['monthly']}</b> ұпай\n"
        f"📊 Жыл: <b>{stats['yearly']}</b> ұпай\n"
        f"🏆 Барлығы: <b>{stats['total']}</b> ұпай\n"
    )
    await message.answer(text, parse_mode="HTML")