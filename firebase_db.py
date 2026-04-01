"""
firebase_db.py — Firebase Realtime Database moduli
"""
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date
from typing import Optional
import logging

import config

logger = logging.getLogger(__name__)

_initialized = False


def init_firebase():
    global _initialized
    if _initialized:
        return

    cred_dict = json.loads(config.FIREBASE_CREDENTIALS_JSON)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": config.FIREBASE_DATABASE_URL
    })
    _initialized = True
    logger.info("Firebase satti qosyldy")


# ===== USERS =====

def save_user(user_id: int, username: str, first_name: str):
    ref = db.reference(f"users/{user_id}")
    existing = ref.get()
    data = {
        "username": username or "",
        "first_name": first_name or "",
    }
    if not existing:
        data["total_points"] = 0
        data["joined_at"] = datetime.now().isoformat()
    ref.update(data)


def get_user(user_id: int) -> Optional[dict]:
    return db.reference(f"users/{user_id}").get()


def add_user_points(user_id: int, points: int):
    ref = db.reference(f"users/{user_id}/total_points")
    current = ref.get() or 0
    ref.set(current + points)


# ===== QUESTIONS =====

def add_question(text: str, options: list[str], correct_answer: int,
                 category: str, created_by: int) -> str:
    ref = db.reference("questions").push({
        "text": text,
        "options": options,
        "correct_answer": correct_answer,
        "category": category,
        "created_by": created_by,
        "created_at": datetime.now().isoformat(),
        "used": False
    })
    logger.info(f"Zhana suraq qosyldy: {ref.key}")
    return ref.key


def get_unused_question() -> Optional[tuple[str, dict]]:
    ref = db.reference("questions")
    questions = ref.order_by_child("used").equal_to(False).limit_to_first(1).get()
    if not questions:
        return None
    qid, qdata = next(iter(questions.items()))
    return qid, qdata


def mark_question_used(question_id: str):
    db.reference(f"questions/{question_id}/used").set(True)


def get_question(question_id: str) -> Optional[dict]:
    return db.reference(f"questions/{question_id}").get()


def get_all_questions() -> dict:
    return db.reference("questions").get() or {}


def get_unused_count() -> int:
    questions = db.reference("questions").order_by_child("used").equal_to(False).get()
    return len(questions) if questions else 0


def delete_question(question_id: str):
    ref = db.reference(f"questions/{question_id}")
    data = ref.get()
    if data is None:
        raise ValueError(f"Suraq tabylmady: {question_id}")
    ref.delete()
    logger.info(f"Suraq oshirildi: {question_id}")


# ===== DAILY TRACKING =====

def get_today_str() -> str:
    return date.today().isoformat()


def set_daily_question(date_str: str, question_id: str):
    """Eski format — qarapaiyym."""
    db.reference(f"daily/{date_str}").set({
        "question_id": question_id,
        "sent_at": datetime.now().isoformat(),
        "first_correct_user_id": None,
        "answer_count": 0
    })


def set_daily_question_with_shuffle(date_str: str, question_id: str,
                                     shuffled_options: list[str],
                                     correct_index: int):
    """Zhana format — shuffled varianttardy saqtaydy."""
    db.reference(f"daily/{date_str}").set({
        "question_id": question_id,
        "sent_at": datetime.now().isoformat(),
        "first_correct_user_id": None,
        "answer_count": 0,
        "shuffled_options": shuffled_options,
        "correct_index": correct_index
    })


def get_daily_question(date_str: str) -> Optional[dict]:
    return db.reference(f"daily/{date_str}").get()


def set_first_correct_user(date_str: str, user_id: int):
    db.reference(f"daily/{date_str}/first_correct_user_id").set(user_id)


def increment_answer_count(date_str: str):
    ref = db.reference(f"daily/{date_str}/answer_count")
    current = ref.get() or 0
    ref.set(current + 1)


# ===== ANSWERS =====

def has_user_answered(date_str: str, question_id: str, user_id: int) -> bool:
    ref = db.reference(f"answers/{date_str}/{question_id}/{user_id}")
    return ref.get() is not None


def save_answer(date_str: str, question_id: str, user_id: int,
                answer: str, is_correct: bool, points: int):
    daily = get_daily_question(date_str)
    order = (daily.get("answer_count", 0) if daily else 0) + 1

    db.reference(f"answers/{date_str}/{question_id}/{user_id}").set({
        "answer": answer,
        "is_correct": is_correct,
        "points": points,
        "answered_at": datetime.now().isoformat(),
        "order": order
    })

    increment_answer_count(date_str)


def get_correct_answers_count(date_str: str, question_id: str) -> int:
    answers = db.reference(f"answers/{date_str}/{question_id}").get()
    if not answers:
        return 0
    return sum(1 for a in answers.values() if a.get("is_correct", False))


# ===== STATS =====

def update_stats(user_id: int, points: int, date_str: str):
    if points <= 0:
        return

    year_month = date_str[:7]
    year = date_str[:4]

    ref_d = db.reference(f"stats/daily/{date_str}/{user_id}/points")
    current_d = ref_d.get() or 0
    ref_d.set(current_d + points)

    ref_m = db.reference(f"stats/monthly/{year_month}/{user_id}/points")
    current_m = ref_m.get() or 0
    ref_m.set(current_m + points)

    ref_y = db.reference(f"stats/yearly/{year}/{user_id}/points")
    current_y = ref_y.get() or 0
    ref_y.set(current_y + points)


def get_top_users(period: str, key: str, limit: int = 10) -> list[tuple[int, int]]:
    data = db.reference(f"stats/{period}/{key}").get()
    if not data:
        return []

    users = [(int(uid), info.get("points", 0)) for uid, info in data.items()]
    users.sort(key=lambda x: x[1], reverse=True)
    return users[:limit]


def get_user_stats(user_id: int) -> dict:
    today = get_today_str()
    year_month = today[:7]
    year = today[:4]

    user = get_user(user_id) or {}
    daily_ref = db.reference(f"stats/daily/{today}/{user_id}/points").get() or 0
    monthly_ref = db.reference(f"stats/monthly/{year_month}/{user_id}/points").get() or 0
    yearly_ref = db.reference(f"stats/yearly/{year}/{user_id}/points").get() or 0

    return {
        "total": user.get("total_points", 0),
        "daily": daily_ref,
        "monthly": monthly_ref,
        "yearly": yearly_ref,
        "username": user.get("username", ""),
        "first_name": user.get("first_name", ""),
    }


# ===== SCHEDULER STATE =====

def get_scheduler_state() -> Optional[dict]:
    return db.reference("scheduler").get()


def set_scheduler_state(last_date: str, selected_hour: int):
    db.reference("scheduler").set({
        "last_question_date": last_date,
        "selected_hour": selected_hour
    })
