from openai import OpenAI


#from updated_embeddings import OAIEmbedding
from config import OPENAI_API_KEY


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


