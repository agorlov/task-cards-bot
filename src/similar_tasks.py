import numpy as np

from .oai_embedding import OAIEmbedding


class SimilarTasks:
    """
    Поиск похожих задач на основе эмбеддингов в таблице tasks.embedding
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
    
