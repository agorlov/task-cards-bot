"""
Приветствие, чтобы напомнить о себе, замотивировать
отправляет рандомную цитату в 19:00 (...не по МСК)
"""
import telebot
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import random
from datetime import datetime

from config import TOKEN, DBCONN
from middlewarebot import MiddlewareBot

# TeleBot (мидл-варе умеет логировать)
bot = MiddlewareBot(TOKEN)

# DB Postgres connection
db = psycopg2.connect(
    dbname=DBCONN['dbname'],
    user=DBCONN['user'],
    password=DBCONN['password'],
    host=DBCONN['host'],
    port=DBCONN['port']
)
db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)


def users():
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT * FROM users WHERE hello_failure_count < 3")
        result = cursor.fetchall()
        return result

quotes = [
    "Привет! 👋",
    "Делу время, потехе час. ⏰",
    "Путь в тысячу ли начинается с первого шага. 🚶",
    "Не откладывай на завтра то, что можешь сделать сегодня. 🌞",
    "Не бойся идти медленно, бойся стоять на месте. 🐢",
    "„Каждый мечтает изменить мир, но никто не ставит целью изменить самого себя.“ — Лев Николаевич Толстой 🌍",
    "„Вдохновение — это умение приводить себя в рабочее состояние.“ — А.С. Пушкин ✍",
    "Лучший способ предсказать будущее - создать его 🔮",
    "Не зацикливайтесь на прошлом - вас там больше не будет. 🔙",
    "„Идиоты делают то, что им не нравится. Умные люди делают то, что любят делать. Гении могут с радостью делать то, что необходимо“ — Садхгуру",
    "Если каждым своим действием вы создаете что-то, что для вас важно, ваша Жизнь Прекрасна, независимо от того, получите вы что-нибудь от этого или нет.“ — Садхгуру",
    "«Верь в мечту. У неё есть приятная особенность — сбываться». — Виталий Гиберт.",
    "„Начинай с малого, но мечтай о великом. Не занимайся одновременно слишком многими вещами. Займись сначала немногими простыми делами, и постепенно переходи к более сложным. И всегда думай о будущем.“ —  Стив Джобс",
    "Совет бота: если ты что-то придумал или увидел возможность, запиши сразу это в виде дела. Пусть мысль полежит и **не будет занимать голову**, придет время и можно будет ей заняться.",
    """
    Выгрузка из головы🧠
    Задача одна - вылить на бумагу или в заметки все дела, что роятся в голове.🐝
    Они тянут нашу энергию и забивают нашу "оперативную память": сделать, купить, оплатить, вернуть, найти... 🤯
    """,
    "Совет бота: если задача оказалась сложной или продолжительной, советую сделать часть, завершить и создай новую задачу или несколько новых задач в продолжение текущей.",
    "Совет бота: делай здачи небольшими или разбивай их на подзадачи, так будет приятнее их завершать и больше мотивации продолжать",
    "Совет бота: «Съесть слона по частям». Декомпозиция это когда крупная задача разделяется на составляющие части."
]

for user in users():
    quote = random.choice(quotes)

    #msg = f"Привет ✨, для вдохновения:\n{quote}"
    msg = f"{quote}"
    try:
        message = bot.send_message(user['telegram_id'], msg)
        res = f"{msg}\n OK! ID: {message.message_id}"
    except telebot.apihelper.ApiException as e:
        res = f"{msg}\n Ошибка отправки: {e}"
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users 
                SET hello_failure_count = hello_failure_count + 1, hello_failure_date = %s 
                WHERE telegram_id = %s
                """,
                (datetime.now(), user['telegram_id'])
            )

    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(f"{current_datetime}: {res}")
