from .oai_embedding import OAIEmbedding
import logging


class UpdatedEmbeddings:
    """
    Обновленные эмбеддинги для задач
    """
    def __init__(self, db) -> None:
        self.db = db
        self.task_emb = OAIEmbedding()

    def update_embeddins(self):
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT task_number, owner_id, task_text
            FROM tasks
            WHERE status = 'ожидает выполнения' AND embedding IS NULL
        """)
        tasks = cursor.fetchall()
        cursor.close()

        number_of_tasks = len(tasks)
        if number_of_tasks > 0:
            logging.info(f'Обновляю эмбеддинги для {number_of_tasks} задач')
        else:
            logging.info(f'Все эмбеддинги обновлены, ничего не делаю')

        for task in tasks:
            task_id, user_id, task_text = task
            self.task_emb.save_for_task(task_id, user_id, task_text, self.db)
            logging.info('Сохраняю эмбеддинг для задачи %s пользователя %s', task_id, user_id)


