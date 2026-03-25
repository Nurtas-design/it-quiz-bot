"""
handlers/quiz.py — Сұрақ жауаптарын өңдеу
"""

import logging
from aiogram import Router, types, F

import config
import firebase_db as fdb

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("answer_"))
async def process_answer_callback(callback: types.CallbackQuery):

    chat_id = callback.message.chat.id
    if chat_id not in config.ALLOWED_CHAT_IDS:
        await callback.answer("⛔ Бұл чатта жұмыс істемейді.", show_alert=True)
        return

    user = callback.from_user
    if not user:
        await callback.answer("❌ Қолданушы анықталмады.", show_alert=True)
        return

    user_id = user.id

    if user.is_bot:
        await callback.answer("⚠️ Боттар жауап бере алмайды.", show_alert=True)
        return

    today = fdb.get_today_str()

    daily = fdb.get_daily_question(today)
    if not daily:
        await callback.answer("ℹ️ Бүгін сұрақ жоқ.", show_alert=True)
        return

    # Skip тексеру
    if daily.get("skipped", False):
        await callback.answer("⏭ Бұл сұрақ өткізілді.", show_alert=True)
        return

    question_id = daily["question_id"]

    if fdb.has_user_answered(today, question_id, user_id):
        await callback.answer("⚠️ Сіз бұрын жауап бердіңіз!", show_alert=True)
        return

    try:
        selected_index = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Қате деректер.", show_alert=True)
        return

    # Daily-ден shuffled деректерді алу
    shuffled_options = daily.get("shuffled_options")
    correct_index = daily.get("correct_index")

    if shuffled_options is not None and correct_index is not None:
        is_correct = selected_index == correct_index
        correct_text = shuffled_options[correct_index]
    else:
        question = fdb.get_question(question_id)
        if not question:
            await callback.answer("❌ Сұрақ табылмады.", show_alert=True)
            return
        correct_index = question["correct_answer"]
        is_correct = selected_index == correct_index
        correct_text = question["options"][correct_index]

    letters = ["A", "B", "C", "D"]

    fdb.save_user(user_id, user.username, user.first_name)

    points = 0
    if is_correct:
        correct_count = fdb.get_correct_answers_count(today, question_id)
        if correct_count == 0:
            points = config.FIRST_CORRECT_POINTS
            fdb.set_first_correct_user(today, user_id)
        else:
            points = config.OTHER_CORRECT_POINTS
    else:
        points = config.WRONG_POINTS

    fdb.save_answer(
        date_str=today,
        question_id=question_id,
        user_id=user_id,
        answer=letters[selected_index],
        is_correct=is_correct,
        points=points
    )

    if points > 0:
        fdb.add_user_points(user_id, points)
        fdb.update_stats(user_id, points, today)

    name = user.first_name or user.username or "Қолданушы"

    # Popup — тек адамға жеке
    if is_correct:
        if points == config.FIRST_CORRECT_POINTS:
            popup_text = f"✅ Дұрыс жауап! Бірінші болдыңыз! +{points} ұпай"
        else:
            popup_text = f"✅ Дұрыс жауап! +{points} ұпай"
    else:
        correct_letter = letters[correct_index]
        popup_text = f"❌ Қате! Дұрыс жауап: {correct_letter}) {correct_text}"

    await callback.answer(popup_text, show_alert=True)

    # Топта — тек дұрыс жауапта
    if is_correct:
        if points == config.FIRST_CORRECT_POINTS:
            group_msg = f"🎉 {name} — бірінші дұрыс жауап берді! +{points} ұпай"
        else:
            group_msg = f"✅ {name} дұрыс жауап берді! +{points} ұпай"
        try:
            await callback.message.answer(group_msg)
        except Exception as e:
            logger.error(f"Топқа жіберу қатесі: {e}")