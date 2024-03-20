"""
Поиск схожих дел по векторам с эмбединнгами
"""

from openai import OpenAI
import numpy as np
from config import OPENAI_API_KEY


oai = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openai.a505.ru/v1")
#oai = OpenAI(api_key=OPENAI_API_KEY)


texts = [
    "За 3 дела подряд давать повышенный бонус XP",
    "Поискать вдохновляющие фразы и идиомы для hello.py",
    "Разобрать вкладки в Sublimetext",
    "субботник",
    "Посмотреть видео про Мульти-агентность: https://www.youtube.com/watch?v=l00ZB2ZaVO0",
    "продолжить обработку голосовых сообщений whisper.cpp",
    "подключить обогреватель в душевой через умную розетку, для прогрева помещения утром дистанционно",
    "Выводить текст комментариев завершенных дел.",
    "Подумать на тему: после нескольких дел, или после какой-то продолжительности выполненных дел - предлагать конкретные способы релакса.",
    "Когда буду подключать GPT - сделать проверку не пытаемся ли добавить дело, которое уже есть в списке",
    "Поискать пленку для окон и новые жалюзи или занавеску с карнизом",
    "Посмотреть игровую тему HTML5 в telegram: https://core.telegram.org/bots/games",
    "Тему бризеров/вент установок/вентиляции поднять для спальни и кабинета - почитать какие решения есть.",
    "В Боте Анна, настроить, чтоб он не употреблял фразу \"но не забудь\"",
    "Идея бота для обучения быстрому чтению идеально ложится на LLM. Он может давать тексты, мерить скорость проверять на сколько текст воспринят",
    "Whisper (audio2text) Протестировать квантованую q4 или q5 модель small и medium",
    "Придумать, какие блоки должны быть на сайте Грейт-Гардарики (минимально необходимые)",
    "Архив",
    "Ознакомиться с PEP-8, найти его на русском: https://peps.python.org/pep-0008/#imports",
    "Зарефакторить и вынести в виде отдельных команд все остальные по аналогии с StartedTaskController",
    "Подумать над переименованием, т.к. Karma Yoga Bot очень специфичное и не понятное большинству название",
    "Бот для проведения теста на знание английского, от простого к сложному",
    "Закупить два балона кемпинг-газа",
    "Заменить фильтр входной",
    "Почитать про Notcoin - для вознаграждения пользователей",
    "Заказать полотенце-сушитель. Или посмотреть какие крепления для старого полотенцесушителя",
    " третья попытка записать voice проверяем вот запись дела таким способом",
    " купить цветы для жены",
    " Подумать на тему применить G5 для категоризации отдела.",
    " Сделать редактирование дел, особенно после записи войсом.",
    " Настроить реакцию, на нажатие кнопки взять следующее после выполненного дела.",
    "исправить  баг: \"слишком длинное сообщение\" - сейчас срабатывает на команду архив",
    "Купить витамин D",
    "Запланировать 01.09.2024 приём витамина D",
    "Добавить справку в меню бота",
    "Запустить бота на втором имени и придумать имя",
    "Продолжить интеграцию с ChatGPT, см. скрипт testopenai.py: https://platform.openai.com/docs/quickstart?context=python",
]

embeddings = []


def oai_embedding(text: str) -> np.ndarray:
    """Вычисляет эмбединг текста с помощью OpenAI API."""
    response = oai.embeddings.create(input=text, model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

def cosine_similarity(a, b):
    """Вычисляет косинусное сходство между двумя векторами."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_similar_cases(new_case_embedding, existing_cases_embeddings, threshold=0.8):
    """
    Ищет существующие дела, похожие на новое дело.
    
    :param new_case_embedding: Эмбеддинг нового дела.
    :param existing_cases_embeddings: Список эмбеддингов существующих дел.
    :param threshold: Порог сходства для определения похожести.
    :return: Список индексов похожих дел.
    """
    similar_cases = []
    for i, existing_embedding in enumerate(existing_cases_embeddings):
        similarity = cosine_similarity(new_case_embedding, existing_embedding)
        if similarity > threshold:
            similar_cases.append(i)
            print(f"{i} => {similarity}")
    return similar_cases


# для каждого дело посчитать embedding
for text in texts:
    embeddings.append(oai_embedding(text))

# Для входной фразы посчитать embedding
test_phrase = "Витамину D закупить"
test_embedding = oai_embedding(test_phrase)

# поискать test_embedding по массиву embedding по сходству по косинусному расстоянию
similar_cases = find_similar_cases(test_embedding, embeddings, threshold=0.9)

# Вывести похожие дела
print("Похожие дела:")
for i in similar_cases:
    print(texts[i])
