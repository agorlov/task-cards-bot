import psycopg2.extras
from .task import Task

class PausedTask:
    """
    Задача в паузе, которая сейчас выполняется у пользоваетля
    """
    def __init__(self, user_id, db):
        self.user_id = user_id
        self.db = db

    def pause(self):
        """
        Поставить задачу на паузу

        Найти задачу в работе, поставить её на паузу и вернуть Task
        а если задачи нет, вернуть None
        """        
        with self.db.cursor() as cursor:
            # Поиск задачи в работе для пользователя
            cursor.execute(
                """
                SELECT task_number
                FROM tasks
                WHERE status = 'в работе' AND owner_id = %s
                LIMIT 1
                """,
                (self.user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            # Обновление статуса задачи на "на паузе"
            cursor.execute(
                """
                UPDATE tasks
                SET status = 'на паузе',
                    start_time = NULL
                WHERE task_number = %s AND owner_id = %s
                """,
                (row[0], self.user_id)
            )
            self.db.commit()
            return Task(row[0], self.user_id, self.db)
