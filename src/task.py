import psycopg2.extras

class Task:
    """
    Задача из БД
    
    В конструктор получает id задачи и базу данных, включает метод task,
    возвращающий словарь с информацией о задаче
    """
    def __init__(self, task_id, user_id, db):
        self.task_id = task_id
        self.user_id = user_id
        self.db = db

    def task(self):
        with self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM tasks WHERE task_number=%s AND owner_id=%s",
                (self.task_id, self.user_id)
            )
            task = cursor.fetchone()
        return task
