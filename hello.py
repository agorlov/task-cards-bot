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
import logging

from config import TOKEN, DBCONN
from middlewarebot import MiddlewareBot

# Настройка базовой конфигурации логирования
logging.basicConfig(filename='app.log',  # Указываем файл для записи логов
                    level=logging.DEBUG,  # Уровень логирования
                    format='%(asctime)s %(message)s',  # Формат сообщений
                    datefmt='%d/%m %H:%M:%S')  # Формат времени


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
    "Совет бота: «Съесть слона по частям». Декомпозиция это когда крупная задача разделяется на составляющие части.",
    "Совет, как снять напряжение: Глубкое дыхание - вдохни глубоко через нос в живот, затем грудь на счет 1-2-3-4. Выдыхайте медленно, свистя через губы, считая до 4. Повторите 3-4 раза.",
    "Как отдыхать между делами на работе: пообщаться с коллегами, выпить чай, немного пройтись, посмотреть в окно, подышать глубоко, выпить воды, послушать музыку",
    "Легкость не означает отсутствие усилий, а означает отсутствие напряжения. — Дипак Чопра",
    "Есть три ловушки, которые воруют радость и мир: сожаление о прошлом, тревога за будущее и неблагодарность за настоящее.",
    "На Аллаха надейся, а верблюда привязывай. — поговорка с востока",
    "Когда человек счастлив, он расслаблен и более эффективен, что повышает его шансы на успех.",
    "Парадокс:\n - ищешь счастье, больше шансов достичь успеха.\n - преследушь успех, меньше шансов на успех и счастье.",
    "«Если вы не делаете того, что не можете, — это не проблема. Но если вы не делаете того, что сделать можете, ваша жизнь – катастрофа». – Садхгуру",
    "Вы достигаете чего-то не потому, что этого желаете, а потому, что делаете Правильные Вещи и получаете необходимые способности. – Садхгуру",
    "«Дисциплина не означает контроль. Это разумность, позволяющая делать именно то, что необходимо». – Садхгуру",
    "Если есть стремление все остальное выстроится само собой. Рай и ад будут работать на вас. – Садхгуру",
    "Дело не в том что именно вы делаете, а в том что вы делаете это не сворачивая с пути. – Садхгуру",
    """
    Чем бы вы ни хотели заниматься в жизни, вы должны привести себя
    к моменту радости и ясности внутри. И чтобы вы ни решили в этот 
    момент, вы должны придерживаться этого. – Садхгуру
    """,
    "«Дисциплина – мать любой победы.» – А.В. Суворов",
    "Собирай по ягодке – наберешь кузовок. (пословица)"
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
    
    logging.info(res)
