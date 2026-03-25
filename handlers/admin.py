"""
handlers/admin.py — Админ командалары
"""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import firebase_db as fdb
from services.question_sender import send_daily_question

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


def is_private(message: types.Message) -> bool:
    return message.chat.type == "private"


class AddQuestionStates(StatesGroup):
    waiting_question_text = State()
    waiting_option_a = State()
    waiting_option_b = State()
    waiting_option_c = State()
    waiting_option_d = State()
    waiting_correct_answer = State()
    waiting_category = State()


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    if not is_private(message):
        return
    current = await state.get_state()
    if current is None:
        await message.answer("ℹ️ Белсенді процесс жоқ.")
        return
    await state.clear()
    await message.answer("❌ Бас тартылды.")


@router.message(Command("test"))
async def cmd_test(message: types.Message):
    if not is_private(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Сізде құқық жоқ.")
        return

    today = fdb.get_today_str()
    daily = fdb.get_daily_question(today)
    if daily:
        from firebase_admin import db as fb_db
        fb_db.reference(f"daily/{today}").delete()
        await message.answer("🗑 Бүгінгі сұрақ тазаланды. Жаңасы жіберілуде...")
    else:
        await message.answer("📤 Сұрақ жіберілуде...")

    bot = message.bot
    success = await send_daily_question(bot)

    if success:
        await message.answer("✅ Сұрақ топқа жіберілді! Топтан қараңыз.")
    else:
        unused = fdb.get_unused_count()
        await message.answer(
            f"❌ Сұрақ жіберілмеді!\n"
            f"📊 Пайдаланылмаған сұрақтар: {unused}\n\n"
            f"Егер 0 болса — /addquestion арқылы сұрақ қосыңыз."
        )


@router.message(Command("addquestion"))
async def cmd_add_question(message: types.Message, state: FSMContext):
    if not is_private(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Сізде құқық жоқ.")
        return

    await state.clear()
    await state.set_state(AddQuestionStates.waiting_question_text)
    await message.answer(
        "📝 <b>Жаңа сұрақ қосу</b>\n\n"
        "Қадам 1/7: Сұрақ мәтінін жазыңыз:\n\n"
        "Бас тарту: /cancel",
        parse_mode="HTML"
    )


@router.message(AddQuestionStates.waiting_question_text)
async def process_question_text(message: types.Message, state: FSMContext):
    if not is_private(message):
        return
    await state.update_data(question_text=message.text)
    await state.set_state(AddQuestionStates.waiting_option_a)
    await message.answer("✅ Қадам 2/7: <b>A</b> вариантын жазыңыз:", parse_mode="HTML")


@router.message(AddQuestionStates.waiting_option_a)
async def process_option_a(message: types.Message, state: FSMContext):
    if not is_private(message):
        return
    await state.update_data(option_a=message.text)
    await state.set_state(AddQuestionStates.waiting_option_b)
    await message.answer("✅ Қадам 3/7: <b>B</b> вариантын жазыңыз:", parse_mode="HTML")


@router.message(AddQuestionStates.waiting_option_b)
async def process_option_b(message: types.Message, state: FSMContext):
    if not is_private(message):
        return
    await state.update_data(option_b=message.text)
    await state.set_state(AddQuestionStates.waiting_option_c)
    await message.answer("✅ Қадам 4/7: <b>C</b> вариантын жазыңыз:", parse_mode="HTML")


@router.message(AddQuestionStates.waiting_option_c)
async def process_option_c(message: types.Message, state: FSMContext):
    if not is_private(message):
        return
    await state.update_data(option_c=message.text)
    await state.set_state(AddQuestionStates.waiting_option_d)
    await message.answer("✅ Қадам 5/7: <b>D</b> вариантын жазыңыз:", parse_mode="HTML")


@router.message(AddQuestionStates.waiting_option_d)
async def process_option_d(message: types.Message, state: FSMContext):
    if not is_private(message):
        return
    await state.update_data(option_d=message.text)
    await state.set_state(AddQuestionStates.waiting_correct_answer)

    data = await state.get_data()
    await message.answer(
        "✅ Қадам 6/7: <b>Дұрыс жауапты</b> таңдаңыз (A, B, C немесе D):\n\n"
        f"A) {data['option_a']}\n"
        f"B) {data['option_b']}\n"
        f"C) {data['option_c']}\n"
        f"D) {data['option_d']}",
        parse_mode="HTML"
    )


@router.message(AddQuestionStates.waiting_correct_answer)
async def process_correct_answer(message: types.Message, state: FSMContext):
    if not is_private(message):
        return

    answer = message.text.strip().upper()
    if answer not in ("A", "B", "C", "D"):
        await message.answer("⚠️ Тек A, B, C немесе D жазыңыз!")
        return

    answer_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    await state.update_data(correct_answer=answer_map[answer])
    await state.set_state(AddQuestionStates.waiting_category)
    await message.answer(
        "✅ Қадам 7/7: <b>Категорияны</b> жазыңыз:\n"
        "(мысалы: Python, JavaScript, Алгоритм, Желі, ОЖ, Деректер қоры)",
        parse_mode="HTML"
    )


@router.message(AddQuestionStates.waiting_category)
async def process_category(message: types.Message, state: FSMContext):
    if not is_private(message):
        return

    data = await state.get_data()
    category = message.text.strip()

    options = [data["option_a"], data["option_b"], data["option_c"], data["option_d"]]
    correct_idx = data["correct_answer"]

    try:
        question_id = fdb.add_question(
            text=data["question_text"],
            options=options,
            correct_answer=correct_idx,
            category=category,
            created_by=message.from_user.id
        )

        correct_letter = ["A", "B", "C", "D"][correct_idx]
        unused_count = fdb.get_unused_count()

        await message.answer(
            "✅ <b>Сұрақ сәтті қосылды!</b>\n\n"
            f"📝 {data['question_text']}\n\n"
            f"A) {options[0]}\n"
            f"B) {options[1]}\n"
            f"C) {options[2]}\n"
            f"D) {options[3]}\n\n"
            f"✅ Дұрыс жауап: <b>{correct_letter}</b>\n"
            f"📂 Категория: {category}\n"
            f"🆔 ID: <code>{question_id}</code>\n\n"
            f"📊 Пайдаланылмаған сұрақтар: <b>{unused_count}</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Сұрақ қосу қатесі: {e}")
        await message.answer(f"❌ Қате: {e}")

    await state.clear()


@router.message(Command("delquestion"))
async def cmd_del_question(message: types.Message):
    if not is_private(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Сізде құқық жоқ.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "🗑 <b>Сұрақты өшіру</b>\n\n"
            "Формат: <code>/delquestion СҰРАҚ_ID</code>\n\n"
            "ID-ні /listquestions арқылы көре аласыз.",
            parse_mode="HTML"
        )
        return

    question_id = parts[1].strip()

    question = fdb.get_question(question_id)
    if not question:
        await message.answer(f"❌ Сұрақ табылмады: <code>{question_id}</code>", parse_mode="HTML")
        return

    try:
        fdb.delete_question(question_id)
        letters = ["A", "B", "C", "D"]
        correct_letter = letters[question.get("correct_answer", 0)]

        await message.answer(
            "✅ <b>Сұрақ өшірілді!</b>\n\n"
            f"📝 {question['text']}\n"
            f"✅ Дұрыс жауап: {correct_letter}\n"
            f"🆔 ID: <code>{question_id}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Сұрақ өшіру қатесі: {e}")
        await message.answer(f"❌ Қате: {e}")


@router.message(Command("listquestions"))
async def cmd_list_questions(message: types.Message):
    if not is_private(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Сізде құқық жоқ.")
        return

    all_questions = fdb.get_all_questions()
    if not all_questions:
        await message.answer("📭 Сұрақтар жоқ. /addquestion арқылы қосыңыз.")
        return

    items = list(all_questions.items())
    total = len(items)
    show_items = items[-20:]

    letters = ["A", "B", "C", "D"]
    text = f"📋 <b>Сұрақтар тізімі</b> (соңғы 20 / барлығы {total})\n\n"

    for i, (qid, q) in enumerate(show_items, 1):
        used = "✅" if q.get("used", False) else "🆕"
        correct = letters[q.get("correct_answer", 0)]
        cat = q.get("category", "?")
        q_text = q.get("text", "")[:60]

        text += (
            f"<b>{i}.</b> {used} [{cat}]\n"
            f"   {q_text}...\n"
            f"   Жауап: {correct} | ID: <code>{qid}</code>\n\n"
        )

    text += (
        "✅ = пайдаланылған, 🆕 = пайдаланылмаған\n\n"
        "🗑 Өшіру: <code>/delquestion ID</code>"
    )

    if len(text) > 4000:
        mid = len(text) // 2
        split_pos = text.rfind("\n\n", 0, mid)
        if split_pos == -1:
            split_pos = mid
        await message.answer(text[:split_pos], parse_mode="HTML")
        await message.answer(text[split_pos:], parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")


@router.message(Command("skip"))
async def cmd_skip(message: types.Message):
    """Бүгінгі сұрақты өткізу — топтағы хабарды да өшіреді."""
    if not is_private(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Сізде құқық жоқ.")
        return

    today = fdb.get_today_str()
    daily = fdb.get_daily_question(today)

    if not daily:
        await message.answer("ℹ️ Бүгін сұрақ әлі жіберілмеген.")
        return

    # Daily-ді skip деп белгілеу
    from firebase_admin import db as fb_db
    fb_db.reference(f"daily/{today}/skipped").set(True)

    await message.answer("⏭ Бүгінгі сұрақ өткізілді. Ешкім жауап бере алмайды.")


@router.message(Command("questioncount"))
async def cmd_question_count(message: types.Message):
    if not is_private(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Сізде құқық жоқ.")
        return

    total = len(fdb.get_all_questions())
    unused = fdb.get_unused_count()

    await message.answer(
        f"📊 <b>Сұрақтар статистикасы</b>\n\n"
        f"📝 Жалпы: <b>{total}</b>\n"
        f"🆕 Пайдаланылмаған: <b>{unused}</b>\n"
        f"✅ Пайдаланылған: <b>{total - unused}</b>",
        parse_mode="HTML"
    )