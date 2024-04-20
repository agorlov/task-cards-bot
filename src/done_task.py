import datetime
from datetime import datetime
from telebot import types

from .user_score import UserScore
from .done_compliment import DoneCompliment
from .basic_keyboard import BasicKeyboard

class DoneTask:
    """
    Завершенная задача, которая сейчас выполняется у пользоваетля
    """

    def __init__(self, db, bot, user_id) -> None:
        self.db = db
        self.bot = bot
        self.user_id = user_id
        self.user_score = UserScore(user_id, db)
        self.basic_keyboard = BasicKeyboard()


    def done_task(self, chat_id, completion_comment=None):
        """
        Отметить текущую задачу как выполненную и обновить баллы пользователя

        :param chat_id: ID чата
        :param completion_comment: Комментарий к выполненной задаче
        """
        
        cursor = self.db.cursor()

        # Выбор задачи со статусом "в работе"
        cursor.execute(
            """
            SELECT
                task_number, task_text, start_time
            FROM tasks
            WHERE status in ('в работе', 'на паузе') AND owner_id = %s
            LIMIT 1
            """,
            (self.user_id,)
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
                (completion_comment, task_number, self.user_id,)
            )
            cursor.close()

            end_time = datetime.now()

            time_taken = (end_time - start_time).total_seconds() / 60

            
            today_count = len(self.done_today())
            # если today_count делится на 3 (комбо из 3х задач), то увеличиваем баллы на 15
            if today_count % 3:
                bonus_str = "✨"
                bonus = 15
            else:
                bonus_str = "✨3x КОМБО🚀" 
                bonus = 30

            self.user_score.update_score(bonus)

            # Кнопки:
            markup = types.InlineKeyboardMarkup(row_width=3)
            btn1 = types.InlineKeyboardButton('Взять следующее', callback_data='new_task')
            btn2 = types.InlineKeyboardButton(
                'Запланировать повторно', callback_data='plan_task_' + str(task_number)
            )
            markup.add(btn1, btn2)

            done_compliment = DoneCompliment().compliment()

            self.bot.send_message(
                chat_id,
                f"{done_compliment} [{bonus_str} +{bonus} XP], за {time_taken:.0f} мин",
                parse_mode="Markdown",
                reply_markup=markup
            )

        else:
            self.bot.send_message(
                chat_id,
                "В данный момент в работе задач нет, показать список? /list",
                reply_markup=self.basic_keyboard.menu()
            )

    def done_today(self):
        """
        Список завершенных задач за сегодня пользователем
        """
        cursor = self.db.cursor()

        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            """
            SELECT
                task_number, task_text, completion_comment
            FROM tasks
            WHERE owner_id = %s AND status = 'завершена' AND date(end_time) = %s
            """,
            (self.user_id, today)
        )

        return cursor.fetchall()            