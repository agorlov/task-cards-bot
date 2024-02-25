import random
import traceback

class StartedTaskController:
    """
    Выбрать дело и начать его

    Отрабатывает команду "дело", выбирает для пользователя задачу и запускает её
    Если уже есть запущенное задание, то выдает сообщение "У вас уже есть задача в работе."
    Если есть задача на паузе, то продолжает работу над ней.

    Author: Alexander Gorlov
    """    
    def __init__(self, db, bot, message):
        self.bot = bot
        self.db = db
        self.message = message

    def startTask(self):
        """
        Начать работу над задачей
        """

        message = self.message
        bot = self.bot
        db = self.db

        user_id = message.from_user.id
        cursor = db.cursor()
        
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE
                status IN ('в работе')
                AND owner_id = %s
            """,
            (user_id,)
        )
        count_in_progress = cursor.fetchone()[0]
        
        if count_in_progress > 0:
            bot.send_message(message.chat.id, "У вас уже есть задача в работе.")
            return
        

        cursor.execute(
            """
            SELECT task_number, task_text
            FROM tasks
            WHERE
                status IN ('ожидает выполнения', 'на паузе')
                AND owner_id = %s
                AND planned_date <= NOW()
            """,
            (user_id,)
        )
        available_tasks = cursor.fetchall()
        
        if len(available_tasks) <= 0:
            bot.send_message(
                message.chat.id, 
                "У вас закончились задачи, придумайте новое дело."
            )            
            return

        cursor.execute(
            """
            SELECT task_number, task_text
            FROM tasks
            WHERE
                status IN ('на паузе')
                AND owner_id = %s
                AND planned_date <= NOW()
            """,
            (user_id,)
        )
        paused_task = cursor.fetchall()

        if len(paused_task) > 0:
            task_number, task_text = paused_task[0]
        else:
            task_number, task_text = random.sample(available_tasks, 1)[0]

        task_text = task_text.strip()
        
        cursor.execute(
            """
            UPDATE tasks SET status = 'в работе', start_time = NOW()
            WHERE task_number = %s AND owner_id = %s
            """, 
            (task_number, user_id,)
        )
        cursor.close()
        
        bot.send_message(
            message.chat.id,
            f"{task_text}"
        )


