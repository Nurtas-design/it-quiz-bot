"""
seed_questions.py — Бастапқы IT сұрақтар жинағы (ЖАҢАРТЫЛҒАН)
Дұрыс жауаптар A, B, C, D бойынша біркелкі таратылған.

Қолдану:
  python seed_questions.py
"""

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

load_dotenv()

FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
ADMIN_ID = int(os.getenv("ADMIN_IDS", "0").split(",")[0])

if not FIREBASE_DATABASE_URL or not FIREBASE_CREDENTIALS_PATH:
    print("❌ .env файлында FIREBASE_DATABASE_URL және FIREBASE_CREDENTIALS_PATH толтырыңыз!")
    sys.exit(1)

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})

QUESTIONS = [
    # === Python (дұрыс жауап әр түрлі позицияда) ===
    {
        "text": "Python тілінде list comprehension нәтижесі қандай тип болады?",
        "options": ["tuple", "dict", "list", "set"],
        "correct_answer": 2,  # C
        "category": "Python"
    },
    {
        "text": "Python-да 'self' кілт сөзі нені білдіреді?",
        "options": [
            "Жаңа объект құру",
            "Модульді импорттау",
            "Статикалық метод белгісі",
            "Класстың ағымдағы данасына сілтеме"
        ],
        "correct_answer": 3,  # D
        "category": "Python"
    },
    {
        "text": "Python-да GIL (Global Interpreter Lock) не үшін қажет?",
        "options": [
            "Бір уақытта тек бір thread Python bytecode орындауы үшін",
            "Жадыны оптимизациялау үшін",
            "Файлдарды қорғау үшін",
            "Желілік қосылысты басқару үшін"
        ],
        "correct_answer": 0,  # A
        "category": "Python"
    },
    {
        "text": "Python-да decorator (@) не істейді?",
        "options": [
            "Цикл құрады",
            "Функцияны басқа функциямен орайды",
            "Айнымалыны жариялайды",
            "Қатені ұстайды"
        ],
        "correct_answer": 1,  # B
        "category": "Python"
    },
    {
        "text": "pip freeze командасы не істейді?",
        "options": [
            "Python-ды жаңартады",
            "Кэшті тазалайды",
            "Пакеттерді жояды",
            "Орнатылған пакеттер тізімін көрсетеді"
        ],
        "correct_answer": 3,  # D
        "category": "Python"
    },

    # === JavaScript ===
    {
        "text": "JavaScript-те '===' операторы не тексереді?",
        "options": [
            "Мән мен типті бірге",
            "Тек мәнді",
            "Тек типті",
            "Ссылканы"
        ],
        "correct_answer": 0,  # A
        "category": "JavaScript"
    },
    {
        "text": "JavaScript-те 'closure' дегеніміз не?",
        "options": [
            "Массивті жабу",
            "Браузерді жабу оқиғасы",
            "Функция өзінің сыртқы scope-на қол жеткізе алуы",
            "Цикл түрі"
        ],
        "correct_answer": 2,  # C
        "category": "JavaScript"
    },
    {
        "text": "Node.js қандай JavaScript engine қолданады?",
        "options": ["SpiderMonkey", "Chakra", "Hermes", "V8"],
        "correct_answer": 3,  # D
        "category": "JavaScript"
    },
    {
        "text": "JavaScript-те Promise.all() не істейді?",
        "options": [
            "Promise-ты жояды",
            "Барлық promise-тар аяқталғанын күтеді",
            "Біріншісі аяқталғанын күтеді",
            "Қатені ұстайды"
        ],
        "correct_answer": 1,  # B
        "category": "JavaScript"
    },
    {
        "text": "typeof null нәтижесі JavaScript-те не болады?",
        "options": ["'null'", "'undefined'", "'boolean'", "'object'"],
        "correct_answer": 3,  # D
        "category": "JavaScript"
    },

    # === Алгоритм ===
    {
        "text": "Binary Search алгоритмінің уақыт күрделілігі қандай?",
        "options": ["O(n²)", "O(n)", "O(1)", "O(log n)"],
        "correct_answer": 3,  # D
        "category": "Алгоритм"
    },
    {
        "text": "Bubble Sort алгоритмінің ең нашар жағдайдағы күрделілігі?",
        "options": ["O(n²)", "O(n)", "O(n log n)", "O(log n)"],
        "correct_answer": 0,  # A
        "category": "Алгоритм"
    },
    {
        "text": "Stack деректер құрылымының принципі қандай?",
        "options": ["Random", "FIFO", "LILO", "LIFO"],
        "correct_answer": 3,  # D
        "category": "Алгоритм"
    },
    {
        "text": "Hash table-де collision дегеніміз не?",
        "options": [
            "Жадының аяқталуы",
            "Кесте толуы",
            "Екі кілт бірдей индекске түсуі",
            "Деректердің жоғалуы"
        ],
        "correct_answer": 2,  # C
        "category": "Алгоритм"
    },
    {
        "text": "Big O нотациясында O(1) нені білдіреді?",
        "options": [
            "Квадраттық уақыт",
            "Тұрақты уақыт",
            "Сызықтық уақыт",
            "Логарифмдік уақыт"
        ],
        "correct_answer": 1,  # B
        "category": "Алгоритм"
    },

    # === Желі ===
    {
        "text": "HTTP протоколында 404 коды нені білдіреді?",
        "options": [
            "Сәтті сұраныс",
            "Авторизация қажет",
            "Сервер қатесі",
            "Ресурс табылмады"
        ],
        "correct_answer": 3,  # D
        "category": "Желі"
    },
    {
        "text": "DNS сервері қандай функция атқарады?",
        "options": [
            "Домен атын IP мекенжайға аударады",
            "Файлдарды сақтайды",
            "Электрондық пошта жібереді",
            "Вирустардан қорғайды"
        ],
        "correct_answer": 0,  # A
        "category": "Желі"
    },
    {
        "text": "TCP мен UDP арасындағы негізгі айырмашылық?",
        "options": [
            "TCP тек веб үшін, UDP тек ойын үшін",
            "Айырмашылық жоқ",
            "TCP сенімді байланыс орнатады, UDP — жоқ",
            "TCP баяу, UDP жылдам"
        ],
        "correct_answer": 2,  # C
        "category": "Желі"
    },
    {
        "text": "HTTPS протоколында 'S' нені білдіреді?",
        "options": ["Speed", "Simple", "Secure", "Server"],
        "correct_answer": 2,  # C
        "category": "Желі"
    },
    {
        "text": "IP мекенжайдың IPv4 нұсқасы неше бит?",
        "options": ["64 бит", "128 бит", "16 бит", "32 бит"],
        "correct_answer": 3,  # D
        "category": "Желі"
    },

    # === Деректер қоры ===
    {
        "text": "SQL-де JOIN операциясы не үшін қолданылады?",
        "options": [
            "Деректерді сұрыптау үшін",
            "Кестені жою үшін",
            "Индекс құру үшін",
            "Екі немесе одан көп кестені байланыстыру үшін"
        ],
        "correct_answer": 3,  # D
        "category": "Деректер қоры"
    },
    {
        "text": "NoSQL деректер қорына қайсысы жатады?",
        "options": ["PostgreSQL", "MongoDB", "MySQL", "Oracle"],
        "correct_answer": 1,  # B
        "category": "Деректер қоры"
    },
    {
        "text": "ACID принциптерінде 'I' нені білдіреді?",
        "options": ["Index", "Integration", "Information", "Isolation"],
        "correct_answer": 3,  # D
        "category": "Деректер қоры"
    },
    {
        "text": "Firebase Realtime Database қандай деректер форматын қолданады?",
        "options": ["JSON", "XML", "CSV", "SQL"],
        "correct_answer": 0,  # A
        "category": "Деректер қоры"
    },

    # === ОЖ ===
    {
        "text": "Linux жүйесінде файл құқықтарын өзгерту командасы қандай?",
        "options": ["chdir", "chown", "chmod", "chgrp"],
        "correct_answer": 2,  # C
        "category": "ОЖ"
    },
    {
        "text": "Docker контейнері мен виртуалды машинаның айырмашылығы?",
        "options": [
            "Docker тек Windows-та жұмыс істейді",
            "VM жылдамырақ",
            "Айырмашылық жоқ",
            "Контейнер ОЖ ядросын ортақ пайдаланады, VM — жоқ"
        ],
        "correct_answer": 3,  # D
        "category": "ОЖ"
    },

    # === Git ===
    {
        "text": "Git-те 'git stash' командасы не істейді?",
        "options": [
            "Branch жояды",
            "Репозиторийді клондайды",
            "Өзгерістерді уақытша сақтайды",
            "Commit жасайды"
        ],
        "correct_answer": 2,  # C
        "category": "Git"
    },
    {
        "text": "Git-те 'merge conflict' қашан пайда болады?",
        "options": [
            "Екі branch бірдей жолды өзгерткенде",
            "Бос репозиторийде",
            "Commit хабарламасы ұзын болғанда",
            "Интернет жоқ кезде"
        ],
        "correct_answer": 0,  # A
        "category": "Git"
    },

    # === Жалпы IT ===
    {
        "text": "API аббревиатурасы нені білдіреді?",
        "options": [
            "Advanced Programming Interface",
            "Automated Protocol Integration",
            "Application Programming Interface",
            "Applied Program Instruction"
        ],
        "correct_answer": 2,  # C
        "category": "Жалпы IT"
    },
    {
        "text": "Agile методологиясындағы 'Sprint' дегеніміз не?",
        "options": [
            "Документация жазу",
            "Қысқа мерзімді жұмыс итерациясы (1-4 апта)",
            "Бүкіл жобаның мерзімі",
            "Тестілеу кезеңі"
        ],
        "correct_answer": 1,  # B
        "category": "Жалпы IT"
    },
]


def seed():
    ref = db.reference("questions")

    existing = ref.get()
    if existing:
        count = len(existing)
        confirm = input(f"⚠️ Firebase-те {count} сұрақ бар. Ескілерін өшіріп, жаңасын жүктеу керек пе? (y/n): ")
        if confirm.lower() == "y":
            ref.delete()
            print("🗑 Ескі сұрақтар өшірілді.")
        else:
            print("❌ Бас тартылды.")
            return

    print(f"\n📝 {len(QUESTIONS)} сұрақ жүктелуде...\n")

    letters = ["A", "B", "C", "D"]
    for i, q in enumerate(QUESTIONS, 1):
        question_data = {
            "text": q["text"],
            "options": q["options"],
            "correct_answer": q["correct_answer"],
            "category": q["category"],
            "created_by": ADMIN_ID,
            "created_at": datetime.now().isoformat(),
            "used": False
        }

        ref.push(question_data)
        correct = letters[q["correct_answer"]]
        print(f"  ✅ {i:2d}. [{q['category']:15s}] Жауап: {correct} | {q['text'][:50]}...")

    print(f"\n🎉 {len(QUESTIONS)} сұрақ сәтті жүктелді!")


if __name__ == "__main__":
    print("=" * 60)
    print("  🧠 IT Quiz Bot — Сұрақтар жүктеу скрипті")
    print("=" * 60)
    seed()