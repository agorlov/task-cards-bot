"""
Приветствие, чтобы напомнить о себе, замотивировать
отправляет рандомную цитату в 19:00 (...не по МСК)
"""

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import logging

from config import DBCONN
from src.oai_embedding import UpdatedEmbeddings

# Настройка базовой конфигурации логирования
logging.basicConfig(filename='app.log',  # Указываем файл для записи логов
                    level=logging.DEBUG,  # Уровень логирования
                    format='%(asctime)s %(message)s',  # Формат сообщений
                    datefmt='%d/%m %H:%M:%S')  # Формат времени


# DB Postgres connection
db = psycopg2.connect(
    dbname=DBCONN['dbname'],
    user=DBCONN['user'],
    password=DBCONN['password'],
    host=DBCONN['host'],
    port=DBCONN['port']
)
db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

logging.info("updemb.py: запускаю обновление эмбеддингов...")

updated_embeddings = UpdatedEmbeddings(db)
updated_embeddings.update_embeddins()