from openai import OpenAI
import logging
import numpy as np

from config import OPENAI_API_KEY


class SimilarTasks:
    """
    Поиск похожих задач
    """
    def __init__(self, db, user_id) -> None:
        self.db = db
        self.user_id = user_id
    
    def similar(self, task_text):
        cursor = self.db.cursor()
        cursor.execute(
            """
            SELECT task_number, task_text, embedding
            FROM tasks
            WHERE
                status IN ('в работе', 'ожидает выполнения')
                AND owner_id = %s
                AND embedding IS NOT NULL
            """,
            (self.user_id,)
        )
        tasks = cursor.fetchall()
        cursor.close()

        task_emb = np.array(OAIEmbedding().emb(task_text))

        similar = []

        for task in tasks:
            task_number, task_text, embedding = task
            if (self._cosine_similarity(task_emb, np.array(embedding))) > 0.9:
                similar.append((task_number, task_text))

        return similar


        
    
    def _cosine_similarity(self, a, b):
        """Вычисляет косинусное сходство между двумя векторами."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    


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


class OAIEmbedding:
    """
    Получить embedding через API OpenAI
    """
    def __init__(self) -> None:
        self.oai = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openai.a505.ru/v1")

    def emb(self, text):      
        """Вычисляет эмбединг текста с помощью OpenAI API."""
        response = self.oai.embeddings.create(input=text, model="text-embedding-ada-002")
        return response.data[0].embedding
    
    
    def save_for_task(self, task_id, user_id, text, db):
        """
        Сохраняет embedding для задачи
        """
        cursor = db.cursor()
        embedding = self.emb(text)

        cursor.execute(
            "UPDATE tasks SET embedding=%s WHERE task_number=%s AND owner_id=%s",
            (embedding,task_id,user_id)
        )
        cursor.close()


