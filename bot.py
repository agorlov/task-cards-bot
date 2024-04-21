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

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta
from dateutil import parser
import uuid

import logging
import re
from functools import wraps
import json

from config import TOKEN, DBCONN
from middlewarebot import MiddlewareBot

# Whisper.cpp - распознавание войсов
# from whispercpp import Whisper
# Faster-whisper
from faster_whisper import WhisperModel

from src.started_task_controller import StartedTaskController
from src.similar_tasks import SimilarTasks
from src.oai_embedding import OAIEmbedding
from src.oai_taskmeta import OAITaskMeta
from src.task import Task
from src.added_user import AddedUser
from src.user_score import UserScore
from src.basic_keyboard import BasicKeyboard
from src.done_task import DoneTask
from src.paused_task import PausedTask



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
3. **Выбор Бота**: Когда есть время, попроси у Бота дело командой `"дело"` /task Он предложит что-то из списка.
4. **Действуй**: Прими предложение и выполни дело с полной отдачей.
5. **Отчет**: Сообщи о выполнении командой `"Готово"` /done
6. **Отложить**: Если не готов заняться делом сейчас, скажи `"Отложить"` /later
7. **Список Дел**: Узнай, что в списке, командой `"Список"` или /list
8. **Удаление**: Удали задачу командой `"удали номер_дела"` или /delete 123

🌟 *Каждое дело будет делать тебя и мир лучше!* 🌟

/help2 - дополнительные возможности

"""

help_advanced = """
## Другие команды

1. **Выполненные дела**: Узнай что было сделано, командой `"Выполненные"` /history
2. **Дело на будущее** 📆: Запланируй дело после даты: /запланируй дд.мм.гггг текст дела /plan
3. **Пауза**: Можно поставить текущее дело на паузу командой "/пауза" /pause и продолжить командой "/продолжить"
4. **Другое дело**: если задача не подходит, вы не готовы сейчас её брать, есть команда "/другое дело"  /another
5. **Готово с комментом**: Можно указать коммент о результате, когда дело готово: "/готово комментарий о результате"
6. **Отредактировать задачу**: Можно отредактировать задачу командой "/edit номер\_дела новый текст"

"""


def my_middleware_handler(message):
    """
    Middleware function

    Perform your actions here, e.g., logging the message
    Сохраним пользователя и время его последней активности:
    """

    AddedUser(message.from_user, db).add_user()

    # Вывод в лог с датой и временем
    user_id = message.from_user.id
    username = message.from_user.username
    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(f"{current_datetime}: {user_id} {username}> {message.text}")

    # залогируем струкутуру message
    logging.info(f"{user_id} {username}: {message.text}")



# Register the middleware function
bot.middleware_handler(my_middleware_handler)




def exception_handler(func):
    """
    Декоратор для логирования ошибок в обработчиках команд.
    """
    @wraps(func)
    def wrapper(message):
        try:
            return func(message)
        except Exception as e:
            short_uuid = str(uuid.uuid4())[:6]
            logging.error(
                "%s ошибка [msg] '%s': %s",
                short_uuid,
                func.__name__,
                str(e),
                exc_info=True
            )
            bot.send_message(
                message.chat.id,
                f"Произошла ошибка {short_uuid}. Попробуйте повторно, либо напишите @agorlov"
            )
    return wrapper

def exception_btn_handler(func):
    """
    Декоратор для логирования ошибок в обработчиках команд.
    """
    @wraps(func)
    def wrapper(call):
        try:
            return func(call)
        except Exception as e:
            short_uuid = str(uuid.uuid4())[:6]
            logging.error(
                "%s ошибка [btn] '%s': %s",
                short_uuid,
                func.__name__,
                str(e),
                exc_info=True
            )
            bot.send_message(
                call.message.chat.id,
                f"Произошла ошибка. Попробуйте повторно, либо напишите @agorlov\nid={short_uuid}"
            )
    return wrapper


@bot.message_handler(commands=['start'])
@exception_handler
def start_msg(message):

    bot.send_message(
        message.chat.id,
        help_message,
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )


@bot.message_handler(
    func=lambda message: message.text.lower() == "help"
    or message.text.lower() == "/help"
    or message.text.lower() == "справка"
    or message.text.lower() == "помощь"
)
@exception_handler
def help_msg(message):
    """
    Обработка команды /help
    """
    bot.send_message(
        message.chat.id,
        help_message,
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )

@bot.message_handler(commands=['help2'])
@exception_handler
def start_msg(message):
    bot.send_message(
        message.chat.id,
        help_advanced,
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )



# Список
@bot.message_handler(
    func=lambda message: message.text.lower() == "список"
    or message.text.lower() == "список дел"
    or message.text.lower() == "/список"
    or message.text.lower() == "/list"
    or message.text.lower() == "list"
)
@exception_handler
def task_list(message):
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

    score = UserScore(user_id, db).user_score()

    if not tasks:
        response = "В твоем списке нет дел... А может ты уже все сделал?\nЧтобы добавить новое дело, просто напиши его сообщением и оно добавится в список!"
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        return

    # Формирование сообщения с списком задач        
    response = f"Что хотелось бы сделать ({len(tasks)}):\n"
    response_prev = f""
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
        
        # Если заданий больше, чем на 4кб - телеграм будет ругаться, ограничим список задач до 4кб
        if len(response) > 3800 and len(response) < 3950:
            tasks_left = len(tasks) - tasks.index(task) - 1
            response += f"\n\n...в списке ещё дел: {tasks_left} шт."
            break;
        elif len(response) > 3950:
            tasks_left = len(tasks) - tasks.index(task)
            response_prev += f"\n\n...в списке ещё дел: {tasks_left} шт."
            response = response_prev
            break;
        else:
            response_prev = response


    response += f"\n[🏆 <b>{score} XP</b>]"


    # Отправка сообщения с списком задач пользователю
    bot.send_message(
        message.chat.id,
        response,
        parse_mode="HTML",
        reply_markup=BasicKeyboard().menu()
    )



# Список завершенных дел
@bot.message_handler(
        func=lambda message: message.text.lower().startswith("архив")
        or message.text.lower().startswith("/archive")
        or message.text.lower().startswith("/history")
        or message.text.lower().startswith("/архив")
        or message.text.lower().startswith("готовые")
        or message.text.lower().startswith("/готовые")
        or message.text.lower().startswith("выполненные")
        or message.text.lower().startswith("/выполненные")
        or message.text.lower().startswith("завершенные")
        or message.text.lower().startswith("/завершенные")
)
@exception_handler
def done_list(message):
    # Получение идентификатора пользователя из сообщения
    user_id = message.from_user.id

    # Установка соединения с базой данных
    cursor = db.cursor()

    # Выполнение SQL-запроса для получения списка задач пользователя
    cursor.execute(
        """
        SELECT
            task_number, task_text, creation_time,
            start_time, end_time, completion_comment
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
        response_prev = ""
        for task in tasks:
            task_number, task_text, creation_time, start_time, end_time, comment = task

            time_taken = (end_time - start_time).total_seconds() / 60
            
            if current_date != end_time.strftime("%d.%m.%Y"):
                current_date = end_time.strftime("%d.%m.%Y")
                response += f"\n\n{current_date}:\n"  # Добавление даты в качестве заголовка

            response += f"""
    ✅ <b>#{task_number}</b> {task_text} <code>за {time_taken:.0f} мин</code>"""

            if comment:
                response += f"""
            💬 {comment}
            """

            # Если заданий больше, чем на 4кб - телеграм будет ругаться, ограничим список задач до 4кб
            if len(response) > 3800 and len(response) < 3950:
                tasks_left = len(tasks) - tasks.index(task) - 1
                response += f"\n\n...в списке ещё дел: {tasks_left} шт."
                break;
            elif len(response) > 3950:
                tasks_left = len(tasks) - tasks.index(task)
                response_prev += f"\n\n...в списке ещё дел: {tasks_left} шт."
                response = response_prev
                break;
            else:
                response_prev = response

        bot.send_message(
            message.chat.id,
            response,
            parse_mode="HTML",
            reply_markup=BasicKeyboard().menu()
        )



# отложить задачу
@bot.message_handler(
        func=lambda message: message.text.lower() == "отложить"
        or message.text.lower().startswith("/cancel")
        or message.text.lower().startswith("/later")
        or message.text.lower().startswith("/отложить")
)
@exception_handler
def postpone_task(message):
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

        UserScore(user_id, db).update_score(-5) # -5XP

        # Отправьте пользователю сообщение о том, что задача была отложена
        bot.send_message(message.chat.id, 
            f"Отложена [😳 -5 XP]:\n```\n{task_text}\n```", 
            parse_mode="Markdown",
            reply_markup=BasicKeyboard().menu()
        )

    else:
        bot.send_message(message.chat.id, 
            "В данный момент нет задач 'в работе' нет.",
            reply_markup=BasicKeyboard().menu()
        )


# поставить на паузу
@bot.message_handler(
        func=lambda message: message.text.lower() == "пауза"
        or message.text.lower().startswith("/пауза")
        or message.text.lower() == "/pause"
)
@exception_handler
def pause_task(message):   
    pause_controller(message.from_user.id, message.chat.id)


def pause_controller(user_id, chat_id):
    task = PausedTask(user_id, db).pause()

    if not task:
        bot.send_message(
            chat_id,
            "В данный момент нет задач 'в работе' нет.",
            reply_markup=BasicKeyboard().menu()
        )
        return

    task_arr = task.task()

    # Отправьте пользователю сообщение о том, что задача была отложена
    bot.send_message(
        chat_id,
        f"На паузе:\n```\n{task_arr['task_text']}\n```",
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )


# завершить задачу
@bot.message_handler(
        func=lambda message: message.text.lower().startswith("готово")
        or message.text.lower().startswith("/done")
        or message.text.lower().startswith("/готово")
        or message.text.lower().startswith("/сделал")
        or message.text.lower().startswith("сделал")
        or message.text.lower().startswith("/сделала")
        or message.text.lower().startswith("сделала")
        or message.text.lower().startswith("/сделалано")
        or message.text.lower().startswith("сделалано")
)
@exception_handler
def done_task(message):

    user_id = message.from_user.id
    text = message.text
    chat_id = message.chat.id

    try:
        command, completion_comment = text.split(maxsplit=1)
    except ValueError as e:
        completion_comment = None

    
    DoneTask(db, bot, user_id).done_task(chat_id, completion_comment=completion_comment)


@bot.callback_query_handler(func=lambda call: call.data == 'new_task')
@exception_btn_handler
def btn_answer_new_task(call):   
    bot.answer_callback_query(callback_query_id=call.id, text="Ок, минутку..")
    started_task = StartedTaskController(
        db,
        bot,
        call.message.chat.id,
        call.from_user.id
    )
    started_task.startTask()
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('plan_task'))
@exception_btn_handler
def btn_answer_plan_task(call):
    # Получение идентификатора пользователя из сообщения
    user_id = call.from_user.id

    planned_date = datetime.now() + timedelta(days=1)
    task_id = call.data.split('_')[2]

    # Получить задачу с task_id
    cursor = db.cursor()
    cursor.execute(
        "SELECT task_text FROM tasks WHERE task_number = %s AND owner_id = %s",
        (task_id, user_id)
    )
    task_text = cursor.fetchone()[0]
    cursor.close()
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (owner_id, status, task_text, planned_date) VALUES (%s, %s, %s, %s)",
        (user_id, 'ожидает выполнения', task_text, planned_date.strftime("%Y-%m-%d %H:%M:%S"))
        
    )
    cursor.close()

    UserScore(user_id, db).update_score(5) # +5XP
    
    bot.send_message(
        call.message.chat.id,
        f"Готово 👍 +5 XP:\n```\n{task_text}\n```",
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )

    # Сохраним эмбеддинг для задачи (смысловое пространство, для поиска похожих задач)
    task_emb = OAIEmbedding()
    task_emb.save_for_task(task_id, user_id, task_text, db)

    bot.answer_callback_query(call.id)



# взять задачу (или продолжить задачу, если есть какая-то на паузе)
@bot.message_handler(
    func=lambda message: message.text.lower() == "дело"
    or message.text.lower() == "взять дело" 
    or message.text.lower().startswith("/дело")
    or message.text.lower() == "/task"
    or message.text.lower() == "/продолжить"
    or message.text.lower() == "продолжить"
)
@exception_handler
def start_task(message):
    started_task = StartedTaskController(db, bot, message.chat.id, message.from_user.id)
    started_task.startTask()

@bot.callback_query_handler(func=lambda call: call.data == 'done_task_btn')
@exception_btn_handler
def btn_done_task(call):
    """
    Кнопка Готово задачи
    """
    DoneTask(db, bot, call.from_user.id).done_task(call.message.chat.id)

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'pause_task_btn')
@exception_btn_handler
def btn_pause_task(call):
    """
    Кнопка продолжить позже (ставит на паузу)
    """
    pause_controller(call.from_user.id, call.message.chat.id)

    bot.answer_callback_query(call.id)
    


@bot.message_handler(
        func=lambda message: message.text.lower() == "другое дело"
        or message.text.lower().startswith("/другое дело")
        or message.text.lower().startswith("/another")
)
@exception_handler
def other_task(message):

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

    UserScore(user_id, db).update_score(-5) # -5XP

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
            "У тебя закончились задачи, придумайте новое дело."
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


@bot.message_handler(
        func=lambda message: message.text.lower().startswith("удали")
        or message.text.lower().startswith("/удали")
        or message.text.lower().startswith("/delete")
)
@exception_handler
def delete_task(message):

    match = re.search(r'(\d+)', message.text.lower())  # Поиск идентификатора дела
    if match:
        task_number = int(match.group(1))
    else:
        bot.send_message(
            message.chat.id,
            f"Не смог определить номер дела (его можно посмотреть командой /list или 'список')"
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
    bot.send_message(
        message.chat.id,
        f"Дело с номером {task_number} удалено.",
        reply_markup=BasicKeyboard().menu()
    )



@bot.message_handler(
        func=lambda message: message.text.lower().startswith("/запланируй")
        or message.text.lower().startswith("запланируй")
        or message.text.lower().startswith("/plan")
)
@exception_handler
def delayed_task_msg(message):
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
        """
        INSERT INTO tasks (owner_id, status, task_text, planned_date)
        VALUES (%s, %s, %s, %s)
        RETURNING task_number
        """,
        (user_id, 'ожидает выполнения', task_text, planned_date)
    )

    task_id = cursor.fetchone()[0]
    cursor.close()

    UserScore(user_id, db).update_score(5) # +5XP
    
    formatted_date = planned_date.strftime("%d.%m.%Y")
    days_until = (planned_date - datetime.now()).days
    bot.send_message(
        message.chat.id,
        f"Запланировал на 📆 {formatted_date} 👍 +5 XP:\n```\n{task_text}\n```\nчерез **{days_until} дней**",
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )

    # Сохраним эмбеддинг для задачи (смысловое пространство, для поиска похожих задач)
    task_emb = OAIEmbedding()
    task_emb.save_for_task(task_id, user_id, task_text, db)



# Идея: если отвечаем на текст с заданием, то это воспринимается как редактирование
    
# Команда /edit 33 отредактированный текст задачи
@bot.message_handler(commands=['edit'])
@exception_handler
def edit_msg(message):

    match = re.search(r'(\d+)\s+(.+)', message.text)  # Поиск идентификатора дела
    if match:
        task_number = int(match.group(1))
        task_text = match.group(2)
    else:
        bot.send_message(
            message.chat.id,
            f"Не смог определить номер дела (его можно посмотреть командой /list или 'список')",
            reply_markup=BasicKeyboard().menu()
        )
        return
    
    cursor = db.cursor()

    # Выбор задачи со статусом "в работе"
    cursor.execute(
        """
        SELECT
            task_number, task_text
        FROM tasks
        WHERE status = 'ожидает выполнения' AND owner_id = %s AND task_number = %s
        LIMIT 1
        """,
        (message.from_user.id, task_number)
    )
    row = cursor.fetchone()

    if row:
        task_number, src_task_text = row
    else:
        bot.send_message(
            message.chat.id, 
            f"Не нашли дело с номером {task_number} в списке ожидающих.",
            reply_markup=BasicKeyboard().menu()
        )
        return


    # обновить дело новым текстом в таблице tasks, по колонке task_id и owner_id

    cursor.execute(
        "UPDATE tasks SET task_text = %s, embedding=NULL WHERE owner_id = %s AND task_number = %s",
        (task_text, message.from_user.id, task_number)
    )
    cursor.close()
    bot.send_message(
        message.chat.id,
        f"Отредактировано #{task_number}:\n```\nбыло: {src_task_text}\nстало: {task_text}\n```",
        parse_mode="Markdown", reply_markup=BasicKeyboard().menu()
    )



@bot.message_handler()
@exception_handler
def new_task_msg(message):
    try:
        # Прочитаем дело с помощью LLM, на пердмет отложенности
        llm_meta = OAITaskMeta(message.text)
        meta = llm_meta.meta()
        # для отладки отправим пользователю мета-информацию
        bot.send_message(
            message.chat.id,
            f"Мета-информация:\n```\n{json.dumps(meta, indent=2)}\n```",
            parse_mode="Markdown",
            reply_markup=BasicKeyboard().menu()
        )
    except Exception as e:
        meta = {}
        logging.error(
            "При обращении к llm произошла ошибка: %s", str(e),
            exc_info=True
        )
    
    if 'date' in meta and meta['date']:
        message.text = f"/plan {meta['date']} {meta['task_text_without_date']}"
        delayed_task_msg(message)
    else:
        # Добавляем дело
        add_task(message.chat.id, message.from_user.id, message.text, message.message_id)



def add_task(chat_id, user_id, task_text, telegram_message_id):
    # Добавляем дело
        
    # Установка соединения с базой данных
    cursor = db.cursor()

    # Выполнение SQL-запроса для добавления новой задачи
    cursor.execute(
        """
        INSERT INTO tasks (
            telegram_message_id,
            owner_id,
            status,
            task_text,
            planned_date
        ) 
        VALUES (%s,%s, %s, %s, NOW())
        RETURNING task_number;
        """,
        (telegram_message_id, user_id, 'ожидает выполнения', task_text)
    )
    
    task_number = cursor.fetchone()[0]
    cursor.close()

    UserScore(user_id, db).update_score(5) # +5XP

    bot.send_message(
        chat_id,
        f"Записал #{task_number} 👍 +5 XP",
        reply_markup=BasicKeyboard().menu()
    )

    # Закрытие курсора и соединения с базой данных
    cursor.close()

    # Поиск похожих
    sim = SimilarTasks(db, user_id)
    sim_list = sim.similar(task_text)

    if sim_list:
        tasks_str = '\n'.join([f"#{task_number} {task_text}" for task_number, task_text in sim_list])
        bot.send_message(
            chat_id,
            f"🔎 Очень похожие задачи (удалить командой /delete номер):\n{tasks_str}",
            reply_markup=BasicKeyboard().menu()
        )



from multiprocessing import Process

@bot.message_handler(content_types=['voice'])
@exception_handler
def voice_msg(message):
    user_id = message.from_user.id
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f"voice_task_{user_id}.ogg", 'wb') as new_file:
        new_file.write(downloaded_file)
    
    bot.send_message(
        message.chat.id,
        f"Voice принят, обрабатываю... (займет 15-20 секунд) 🎙",
        reply_markup=BasicKeyboard().menu()
    )

    p = Process(
        target=process_voice,
        args=(f"voice_task_{user_id}.ogg", user_id, message.chat.id, message.message_id)
    )
    p.start()

def process_voice(file_name: str, user_id, chat_id, message_id) -> None:
    print("Обработка войса в process_voice...")
    whisper = WhisperModel(
        'small', # medium не влезла в 2Гб доступных на хостинге :(
        device="cpu",
        compute_type="int8",
        download_root="./models"
    )
    
    segments, info = whisper.transcribe(
        file_name,
        beam_size=5,
        language='ru',
        initial_prompt=""
    )
    
    task_text = "\n".join([segment.text for segment in segments])

    add_task(chat_id, user_id, "🎤 " + task_text, message_id)


@bot.edited_message_handler(content_types=['text'])
@exception_handler
def handle_edited_message(message):

    message_id = message.message_id
    # обновить дело новым текстом в таблице tasks, по колонке task_id и owner_id
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET task_text = %s, embedding=NULL WHERE owner_id = %s AND telegram_message_id = %s",
        (message.text, message.from_user.id, message_id)
    )
    cursor.close()
    bot.send_message(
        message.chat.id,
        f"Отредактировано:\n```\n{message.text}\n```",
        parse_mode="Markdown",
        reply_markup=BasicKeyboard().menu()
    )



# Начинаем опрос сервера Telegram
bot.polling()


print("Bot слушает...")
bot.polling(non_stop=True)
