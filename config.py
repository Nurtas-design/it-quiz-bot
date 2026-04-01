"""
config.py — Конфигурация модулі
Барлық .env айнымалыларды жүктейді және валидация жасайды.
"""

import os
import sys
from dotenv import load_dotenv

# .env файлын жүктеу
load_dotenv()


def _get_required(key: str) -> str:
    """Міндетті env айнымалысын алу. Жоқ болса — бағдарламаны тоқтату."""
    value = os.getenv(key)
    if not value:
        print(f"❌ ҚАТЕ: '{key}' .env файлында табылмады!")
        sys.exit(1)
    return value


def _parse_int_list(raw: str) -> list[int]:
    """Үтірмен бөлінген сандар тізімін parse ету."""
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


# ===== Telegram =====
BOT_TOKEN: str = _get_required("BOT_TOKEN")

# ===== Firebase =====
FIREBASE_DATABASE_URL: str = _get_required("FIREBASE_DATABASE_URL")
FIREBASE_CREDENTIALS_JSON: str = _get_required("FIREBASE_CREDENTIALS_JSON")

# ===== Админдер тізімі =====
ADMIN_IDS: list[int] = _parse_int_list(_get_required("ADMIN_IDS"))

# ===== Рұқсат етілген чаттар =====
ALLOWED_CHAT_IDS: list[int] = _parse_int_list(_get_required("ALLOWED_CHAT_IDS"))

# ===== Уақыт белдеуі =====
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Almaty")

# ===== Сұрақ жіберу уақыттары (сағат) =====
QUESTION_HOURS: list[int] = [9, 12, 15, 18, 21]

# ===== Ұпай жүйесі =====
FIRST_CORRECT_POINTS: int = 5   # Бірінші дұрыс жауап
OTHER_CORRECT_POINTS: int = 1   # Қалған дұрыс жауаптар
WRONG_POINTS: int = 0           # Қате жауап
