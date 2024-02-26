"""
Бот для того чтобы легко вспомнить какое-нибудь
полезное дело, для себя или для окружающих, сделать его с полной
отдачей и без ожиданий. B принять результат каким бы он ни был.

Помогает делать, то что иногда хочется отложить, быть деятельным,
делать то о чем можно случайно забыть.

Это такой GTD - Представь себе твои дела, это колода карт,
бот перемешивает её и дает возможность тебе вытянуть карточку.

Автор: Александр Горлов

Todo:
    - Если дело не выполнено в течении дня снимаем его статус.
    - Добавить menu с командами
    - Перенос дел в календарь и из календаря
    - Дело на дату или на время (с напоминанием)
    - Хвалить за выполненные дела
    - Вдохновлять цитатами
    - Вести скор выполненных дел (как в шагах в ВК)
    - Предлагать варианты дел/примеры дел
    - В гитхаб добавить реп


-------
Советы:
Вот вы поработали, скажем 15-20 минут, что-то придумали новое, что делать дальше
можно показать готовность текущей задачи, и сразу создать задачу на продолжение.

ДРугой вариант, вы начали делать и по ходу увидели (например начали прибирать стол),
и увидели стопку неразобранных бумаг. Рекомендуем не браться сразу за новые дела, 
пока не закончено это дело. Лучше добавить новое дело "Разобрат стопку бумаг" и 
закончить текущее дело. 

Выгрузка дел из головы в планировщик - это один из путей как снизить потерю энерги.
Так оставаться в более расслабленном и сконцентрированном состоянии. 
Наверное вы наблюдали когда надо делать несколько дел сразу, или помнить сразу
о многих вещах это нагружает голову.

--------

XP - генерировать на неделю
    Показывать сколько набрали конкуренты за эту неделю
    Если конкурентов нет, то придумать их
    Каждую неделю формировать новую команду по уровню и по темпу,
    на основе данных предыдущей недели.

    Посмотреть как это сделано в Лингва Лео или в brilliant
    
    Возможность добавить друзей для состязаний
    
    Убрать штраф за отложенное дело?

Возможно за дни без дел понижать score на 1.


Отладочный бот:
    https://t.me/karmadev_bot

Продакшен бот:
    https://t.me/karma_yoga_bot

"""

from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
from dateutil import parser

import logging
import random
import re
import traceback

from config import TOKEN, DBCONN
from middlewarebot import MiddlewareBot

from whispercpp import Whisper

from src.started_task_controller import StartedTaskController


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

help_message = """
# 🌟 Добро пожаловать Бот! 🌟

Бот - твой помощник в развитии через действие. Он помогает делать дела без оценок и привязанностей.
В этом заключается возможность для внутреннего развития, в преододлении внутренних ограничений,
для того чтобы делать то что ты сам выбираешь.

## 🔑 Особенность Бота:
- **Вдохновение**: Ты сам придумываешь дела, а Бот помогает выбрать подходящее в данный момент.
- **Ваша задача**: Выполняй их с полной отдачей и без ожиданий.

_Представьте: это GTD (Getting Things Done) с духовной составляющей._

### 🏠 *Идеально подходит для:*
- Для дел по дому
- Добавления дисциплины в жизнь
- Доведения дел до конца


🚀 **Вдохновение на каждый день**:
Я разработал этого Бота, чтобы помочь в решении повседневных задач, повышении самодисциплины и завершении начатого.

## Как это работает:

## 🚀 Как это работает:
1. **Запланируй Дело**: Запиши дела, которые хочешь сделать. Бот их запомнит.
2. **Краткость**: Дела должны быть компактными, старйтесь делить их на 15-30 минут.
3. **Выбор Бота**: Когда есть время, попроси у Бота дело командой `"дело"`. Он предложит что-то из списка.
4. **Действуй**: Прими предложение и выполни дело с полной отдачей.
5. **Отчет**: Сообщи о выполнении командой `"Готово"`.
6. **Отложить**: Если не готов заняться делом сейчас, скажи `"Отложить"`.
7. **Список Дел**: Узнай, что в списке, командой `"Список"`.
8. **Удаление**: Удали задачу командой `"удали #идентификатор_дела"`.

🌟 *Каждое дело будет делать тебя и мир лучше!* 🌟

## Другие команды

1. **Выполненные дела**: Узнай что было сделано, командой `"Выполненные"`
2. **Дело на будущее** 📆: Запланируй дело после даты: /запланируй дд.мм.гггг текст дела
3. **Пауза**: Можно поставить текущее дело на паузу командой "/пауза" и продолжить командой "/продолжить"
4. **Другое дело**: если задача не подходит, вы не готовы сейчас её брать, есть команда "/другое дело" 
5. **Готово с комментом**: Можно указать коммент о результате, когда дело готово: "/готово комментарий о результате"
"""

# текущая дата

# """
# Примеры дел:
# - вынести мусор
# - помыть посуду
# - протереть пыль
# - купить продукты
# - выкинуть просроченнные продукты
# - полить цветы
# - 
# """

# 
# Define your middleware function
def my_middleware_handler(message):
    # Perform your actions here, e.g., logging the message
    # Сохраним пользователя и время его последней активности:
    add_user_to_db(message.from_user)

    # Вывод в лог с датой и временем
    user_id = message.from_user.id
    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(f"{current_datetime}: {user_id}: {message.text}")


# Register the middleware function
bot.middleware_handler(my_middleware_handler)



# Функция для добавления нового пользователя в базу данных
def add_user_to_db(user):
    cursor = db.cursor()

    # Проверка, существует ли пользователь в базе данных
    cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (user.id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        # Добавление нового пользователя
        cursor.execute(
            "INSERT INTO users (telegram_id, username, firstname, lastname) VALUES (%s, %s, %s, %s)",
            (user.id, user.username, user.first_name, user.last_name))
    else:
        # Обновление информации и lastmessage_time для существующего пользователя
        cursor.execute("UPDATE users SET lastmessage = NOW() WHERE telegram_id = %s", (user.id,))

    cursor.close()


def done_compliment():
    # Похвалить за завершенное дело
    compliments = [
        "Отличная работа! 👍",
        "Молодец! 👏",
        "Прекрасно! 💯",
        "Фантастически! 🌟",
        "Великолепно! ✨",
        "Впечатляюще! 🤩",
        "Браво! 👌",
        "Так держать! 💪",
        "Спасибо! 🙌",
        "Благодарю за труд! 🎉",
        "Отлично! 🎉",
        "Возьми 5-10 минут релакса",
        "Потрудился - расслабься, это поддержит энергию! 🔋⚡️😌",
        "Сделал дело - гуляй смело! 🏃‍♂️🍃",
        "А ты давно пил воду? Учерные рекомендуют 7-8 стаканов чистой воды в день. 🌊",
    ]
    return random.choice(compliments)

def update_score(user_id, points):
    # Начисление очков за выполнение дела или за другие действия
    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET karma_score = karma_score + %s WHERE telegram_id = %s",
            (points, user_id)
        )
        cursor.close()
    except Exception as e:
        print(f"Ошибка начисления очков: {e}")

def user_score(user_id):
    # Скор пользователя
    cursor = db.cursor()
    cursor.execute("SELECT karma_score FROM users WHERE telegram_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return 0  # Default score if user not found


@bot.message_handler(commands=['start'])
def start_msg(message):

    bot.send_message(message.chat.id, help_message, parse_mode="Markdown")    


@bot.message_handler(commands=['help'])
def start_msg(message):
    # Обработка команды /help
    bot.send_message(message.chat.id, help_message, parse_mode="Markdown")

# /time
@bot.message_handler(commands=['time'])
def time_msg(message):

    cursor = db.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT NOW()")
    result = cursor.fetchone()

    for key, value in result.items():
        print(f"{key}: {value}")

    cursor.close()

    # Форматирование даты и времени в нужный формат
    nowdate = result['now'].strftime("%d.%m.%Y %H:%M:%S")

    print(message)

    bot.send_message(
        message.chat.id,
        f"""
        Сейчас: {nowdate}
        Дата из сообщения message.date: {message.date}
        """,
        parse_mode='html'
    )
    
    bot.send_message(
        message.chat.id,
        f"Debug info: {vars(message)}",
        parse_mode='html'
    )


# Список
@bot.message_handler(
    func=lambda message: message.text.lower() == "список"
    or message.text.lower().startswith("/список")
)
def task_list(message):
    try:
        # Получение идентификатора пользователя из сообщения
        user_id = message.from_user.id

        # Установка соединения с базой данных
        cursor = db.cursor()

        # Выполнение SQL-запроса для получения списка задач пользователя
        cursor.execute(
            """
            SELECT task_number, task_text, status, creation_time, planned_date
            FROM tasks
            WHERE owner_id = %s AND status IN ('ожидает выполнения', 'в работе', 'на паузе')
            ORDER BY 
                CASE 
                    WHEN status = 'в работе' THEN 1
                    WHEN status = 'на паузе' THEN 2
                    ELSE 3
                END, task_number
            """,
            (user_id,)
        )
        tasks = cursor.fetchall()
        cursor.close()

        score = user_score(user_id)

        if not tasks:
            response = "В твоем списке нет дел... А может ты уже все сделал?\nЧтобы добавить новое дело, просто напиши его сообщением и оно добавится в список!"
            bot.send_message(message.chat.id, response, parse_mode="HTML")
            return

        # Формирование сообщения с списком задач        
        response = f"Что хотелось бы сделать ({len(tasks)}):\n"
        for task in tasks:
            task_number, task_text, status, creation_time, planned_date = task
            creation_time = creation_time.strftime("%d.%m.%Y %H:%M:%S")            
            if status == "в работе":
                task_status = "<b>🚀 В РАБОТЕ</b>: "
            elif status == "на паузе":
                task_status = "<b>⏸️ ПАУЗА </b>: "
            else:
                task_status = ""

            response += f"• {task_status}<b>#{task_number}</b> {task_text} (от {creation_time})\n"

            if planned_date > datetime.now():
                response += f"    📆 на {planned_date.strftime('%d.%m.%Y')}\n"

        response += f"\n[🏆 <b>{score} XP</b>]"


        # Отправка сообщения с списком задач пользователю
        bot.send_message(message.chat.id, response, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")



# Список завершенных дел
@bot.message_handler(
        func=lambda message: message.text.lower().startswith("архив")
        or message.text.lower().startswith("/архив")
        or message.text.lower().startswith("готовые")
        or message.text.lower().startswith("/готовые")
        or message.text.lower().startswith("выполненные")
        or message.text.lower().startswith("/выполненные")
        or message.text.lower().startswith("завершенные")
        or message.text.lower().startswith("/завершенные")
)
def task_list(message):
    try:
        # Получение идентификатора пользователя из сообщения
        user_id = message.from_user.id

        # Установка соединения с базой данных
        cursor = db.cursor()

        # Выполнение SQL-запроса для получения списка задач пользователя
        cursor.execute(
            """
            SELECT task_number, task_text, creation_time, start_time, end_time
            FROM tasks
            WHERE owner_id = %s AND status = 'завершена'
            ORDER BY end_time DESC
            """,
            (user_id,)
        )
        tasks = cursor.fetchall()
        cursor.close()        

        if not tasks:
            response = "В твоем списке нет завершенных дел.\nДобавь новое дело, просто напиши его сообщением и оно добавится в список. По готовности дай команду - готово."
        else:        
            # Формирование сообщения с списком задач
            current_date = None
            response = ""
            for task in tasks:
                task_number, task_text, creation_time, start_time, end_time = task

                time_taken = (end_time - start_time).total_seconds() / 60
                
                if current_date != end_time.strftime("%d.%m.%Y"):
                    current_date = end_time.strftime("%d.%m.%Y")
                    response += f"\n\n{current_date}:\n"  # Добавление даты в качестве заголовка

                response += f"""
            ✅ <b>#{task_number}</b> {task_text} <code>за {time_taken:.0f} мин</code>
                """

        # Отправка сообщения с списком задач пользователю
        bot.send_message(message.chat.id, response, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {traceback.format_exc()}")



# отложить задачу
@bot.message_handler(func=lambda message: message.text.lower() == "отложить" or message.text.lower().startswith("/отложить"))
def postpone_task(message):
    try:
        cursor = db.cursor()

        user_id = message.from_user.id

        # Выбор задачи со статусом "в работе"
        cursor.execute(
            """
            SELECT
                task_number, task_text
            FROM tasks
            WHERE status = 'в работе' AND owner_id = %s
            LIMIT 1
            """,
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            task_number, task_text = row

            # Обновление записи задачи в базе данных
            cursor.execute(
                """
                UPDATE tasks
                SET status = 'ожидает выполнения',
                    postponement_count = postponement_count + 1,
                    start_time = NULL
                WHERE task_number = %s AND owner_id = %s
                """, 
                (task_number, user_id,)
            )            

            # Закройте соединение с базой данных
            cursor.close()

            update_score(user_id, -5) # -5XP

            # Отправьте пользователю сообщение о том, что задача была отложена
            bot.send_message(message.chat.id, 
                f"Отложена [😳 -5 XP]:\n```\n{task_text}\n```", 
                parse_mode="Markdown"
            )

        else:
            bot.send_message(message.chat.id, 
                "В данный момент нет задач 'в работе' нет."
            )

    except Exception as e:
        # Обработка ошибок
        bot.send_message(message.chat.id, 
            f"Произошла ошибка при отложении задачи: {e}"
        )

# поставить на паузу
@bot.message_handler(
        func=lambda message: message.text.lower() == "пауза"
        or message.text.lower().startswith("/пауза")
)
def pause_task(message):
    try:
        cursor = db.cursor()

        user_id = message.from_user.id

        # Выбор задачи со статусом "в работе"
        cursor.execute(
            """
            SELECT
                task_number, task_text
            FROM tasks
            WHERE status = 'в работе' AND owner_id = %s
            LIMIT 1
            """,
            (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            bot.send_message(message.chat.id, "В данный момент нет задач 'в работе' нет.")
            return

        task_number, task_text = row

        # Обновление записи задачи в базе данных
        cursor.execute(
            """
            UPDATE tasks
            SET status = 'на паузе',
                start_time = NULL
            WHERE task_number = %s AND owner_id = %s
            """,
            (task_number, user_id,)
        )
        cursor.close()

        # Отправьте пользователю сообщение о том, что задача была отложена
        bot.send_message(
            message.chat.id,
            f"На паузе:\n```\n{task_text}\n```",
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.send_message(message.chat.id, 
            f"Произошла ошибка (на паузе) задачи: {e}"
        )        

# завершить задачу
@bot.message_handler(
        func=lambda message: message.text.lower().startswith("готово")
        or message.text.lower().startswith("/готово")
        or message.text.lower().startswith("/сделал")
        or message.text.lower().startswith("сделал")
        or message.text.lower().startswith("/сделала")
        or message.text.lower().startswith("сделала")
        or message.text.lower().startswith("/сделалано")
        or message.text.lower().startswith("сделалано")
)
def done_task(message):
    try:
        cursor = db.cursor()

        user_id = message.from_user.id

        try:
            command, completion_comment = message.text.split(maxsplit=1)
        except ValueError as e:
            completion_comment = None

        # Выбор задачи со статусом "в работе"
        cursor.execute(
            """
            SELECT
                task_number, task_text, start_time
            FROM tasks
            WHERE status in ('в работе', 'на паузе') AND owner_id = %s
            LIMIT 1
            """,
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            task_number, task_text, start_time = row

            # Обновление записи задачи в базе данных
            cursor.execute(
                """
                UPDATE tasks 
                SET
                    status = 'завершена',
                    end_time = NOW(),
                    completion_comment = %s
                WHERE task_number = %s AND owner_id = %s
                """,
                (completion_comment, task_number, user_id,)
            )
            cursor.close()

            end_time = datetime.now()

            time_taken = (end_time - start_time).total_seconds() / 60

            # Отправьте пользователю сообщение о том, что задача была отложена
            update_score(user_id, 15)


            # Кнопки:
            markup = types.InlineKeyboardMarkup(row_width=3)
            btn1 = types.InlineKeyboardButton('Взять следующее', callback_data='new_task')
            btn2 = types.InlineKeyboardButton('Запланировать повторно', callback_data='plan_task')
            markup.add(btn1, btn2)

            bot.send_message(
                message.chat.id,
                f"Сделано:\n```\n{task_text}\n```\n{done_compliment()} [✨ +15 XP], за {time_taken:.0f} мин",
                parse_mode="Markdown",
                reply_markup=markup
            )

        else:
            bot.send_message(
                message.chat.id,
                "В данный момент в работе задач нет, показать список? /список"
            )


    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при отложении задачи: {e}")


@bot.callback_query_handler(func=lambda call: call.data == 'new_task')
def btn_answer(call):
    bot.send_message(call.message.chat.id, f"@todo Кнопка ['Взять ещё дело'] нажата.")

@bot.callback_query_handler(func=lambda call: call.data == 'plan_task')
def btn_answer(call):
    bot.send_message(call.message.chat.id, f"@todo Кнопка ['Запланировать повторно'] нажата.")    



# взять задачу (или продолжить задачу, если есть какая-то на паузе)
@bot.message_handler(
    func=lambda message: message.text.lower() == "дело" 
    or message.text.lower().startswith("/дело")
    or message.text.lower() == "/продолжить"
    or message.text.lower() == "продолжить"
)
def start_task(message):
    try:
        started_task = StartedTaskController(db, bot, message)
        started_task.startTask()
    except Exception as e:
        bot.send_message(
            message.chat.id, 
            f"Произошла ошибка при выполнении команды 'дело': {e}\n{traceback.format_exc()}"
        )


@bot.message_handler(
        func=lambda message: message.text.lower() == "другое дело"
        or message.text.lower().startswith("/другое дело")
)
def other_task(message):
    try:
        cursor = db.cursor()

        user_id = message.from_user.id

        # Выбор задачи со статусом "в работе"
        cursor.execute(
            """
            SELECT
                task_number, task_text
            FROM tasks
            WHERE status = 'в работе' AND owner_id = %s
            LIMIT 1
            """,
            (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            bot.send_message(message.chat.id, 
                "В данный момент нет задач 'в работе' нет."
            )
            return
    
        task_number, task_text = row

        # Обновление записи задачи в базе данных
        cursor.execute(
            """
            UPDATE tasks
            SET status = 'ожидает выполнения',
                postponement_count = postponement_count + 1,
                start_time = NULL
            WHERE task_number = %s AND owner_id = %s
            """, 
            (task_number, user_id,)
        )            

        cursor.close()

        update_score(user_id, -5) # -5XP

        bot.send_message(message.chat.id, 
            f"Отложена [😳 -5 XP]:\n```\n{task_text}\n```", 
            parse_mode="Markdown"
        )

        # Выбор другой задачи для пользователя
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT task_number, task_text
            FROM tasks
            WHERE status IN ('ожидает выполнения')
            AND owner_id = %s
            AND planned_date <= NOW()
            AND task_number != %s
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (user_id, task_number,)
        )
        new_task = cursor.fetchone()

        if not new_task:
            bot.send_message(
                message.chat.id, 
                "У вас закончились задачи, придумайте новое дело."
            )        
            return
        
        new_task_number, new_task_text = new_task

        cursor.execute(
            "UPDATE tasks SET status = 'в работе', start_time = NOW() WHERE task_number = %s AND owner_id = %s", 
            (new_task_number, user_id,)
        )
        cursor.close()        

        bot.send_message(message.chat.id, 
            f"Вот новое дело:\n```\n{new_task_text}\n```", 
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}\n{traceback.format_exc()}")


@bot.message_handler(
        func=lambda message: message.text.lower().startswith("удали")
        or message.text.lower().startswith("/удали")
)
def delete_task(message):
    try:
        match = re.search(r'(\d+)', message.text.lower())  # Поиск идентификатора дела
        if match:
            task_number = int(match.group(1))
        else:
            bot.send_message(
                message.chat.id,
                f"Не смог определить номер дела (его можно посмотреть командой /список)"
            )
            return
        
        cursor = db.cursor()

        # Добавляем проверку owner_id из таблицы tasks, чтобы он соответствовал id
        # текущего пользователя телеграм
        cursor.execute("DELETE FROM tasks WHERE task_number = %s AND owner_id = %s", 
                       (task_number, message.from_user.id))
        # db.commit()

        # Закрываем соединение с базой данных
        cursor.close()

        # Отправляем сообщение об успешном удалении дела
        bot.send_message(message.chat.id, f"Дело с номером {task_number} удалено.")

    except Exception as e:
        # Обработка ошибок
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении дела номер={task_number}: {e}")



@bot.message_handler(
        func=lambda message: message.text.lower().startswith("/запланируй")
        or message.text.lower().startswith("запланируй")
)
def delayed_task_msg(message):
    # Добавляем отложенное дело, которое станет актуально начиная с даты
    try:
        # Получение идентификатора пользователя из сообщения
        user_id = message.from_user.id


        try:
            command, date_str, *task_text_parts = message.text.split(maxsplit=2)
            task_text = ' '.join(task_text_parts)
            planned_date = parser.parse(date_str, dayfirst=True)
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"Не разобрал команду. Используй так /запланируй дд.мм.гггг текст_дела_которое_нужно_выполнить\n{e}"
            )
            return
            

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO tasks (owner_id, status, task_text, planned_date) VALUES (%s, %s, %s, %s)",
            (user_id, 'ожидает выполнения', task_text, planned_date)
        )
        cursor.close()


        update_score(user_id, 5) # +5XP
       
        formatted_date = planned_date.strftime("%d.%m.%Y")
        days_until = (planned_date - datetime.now()).days
        bot.send_message(
            message.chat.id,
            f"Запланировал на 📆 {formatted_date} 👍 +5 XP:\n```\n{task_text}\n```\nчерез **{days_until} дней**",
            parse_mode="Markdown"
        )


    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")



@bot.message_handler()
def new_task_msg(message):
    # Добавляем дело
    try:
        # Получение идентификатора пользователя из сообщения
        user_id = message.from_user.id

        # Текст сообщения будет добавлен как новая задача в базу данных
        task_text = message.text

        # Установка соединения с базой данных
        cursor = db.cursor()

        # Выполнение SQL-запроса для добавления новой задачи
        cursor.execute("INSERT INTO tasks (owner_id, status, task_text, planned_date) VALUES (%s, %s, %s, NOW())",
                       (user_id, 'ожидает выполнения', task_text))

        update_score(user_id, 5) # +5XP

        bot.send_message(message.chat.id, f"Записал 👍 +5 XP:\n```\n{task_text}\n```", parse_mode="Markdown") # , reply_markup=markup

        # Закрытие курсора и соединения с базой данных
        cursor.close()


    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")




from multiprocessing import Process

@bot.message_handler(content_types=['voice'])
def voice_msg(message):
    user_id = message.from_user.id
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f"voice_task_{user_id}.ogg", 'wb') as new_file:
        new_file.write(downloaded_file)
    
    bot.send_message(message.chat.id, f"Voice принят, обрабатываю...")

    p = Process(target=process_voice, args=(f"voice_task_{user_id}.ogg", user_id))
    p.start()

def process_voice(file_name, user_id):
    print("Обработка войса в process_voice...")
    w = Whisper('small')
    result = w.transcribe(file_name)
    text = w.extract_text(result)
    bot.send_message(user_id, f"```{text}```")
    print("Обработка войса в process_voice завершена")



print("Bot started listening...")
bot.polling(non_stop=True)