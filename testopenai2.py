from openai import OpenAI

from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openai.a505.ru/v1")

system = """
Ты помогаешь вести список дел. Пользователь предложит текст задачи, ответь на несколько вопросов.

1. Является ли дело повторяемым или регулярным? (например сделать субботник, заменить фильтр воды, протереть пыль)
2. К какой категории относится дело? По аналогии с тем как ставят хештеги в телеграмме или инстаграмме. Постарайся уловить смысл и предложить один или несколько хештегов.
3. Указано ли в деле дата когда дело нужно выполнить? Если да, то выведи дату в формате дд.мм.гггг. Например 12.01.2022. Если в дате год не указан, то пусть будет 2024.
4. Не похоже ли дело на одну из команд или возможно пользователь допустил опечатку команды (примеры команд /list, list, /delete delete, отложить) Команды это одно слово, например "помоги" или "help" или "start"

Результат представь в виде json, например:
```
{
    "repeatable": false,
    "category": "#программирование",
    "date": "12.01.2022",
    "is_command": false,
    "command": null
}
```

ещё пример, когда текст (staart) похож на команду (start):

```
{
    "repeatable": false,
    "category": null,
    "date": null,
    "is_command": true,
    "command": "start"
}
```
"""

examples = [
    "staart",
    "помыть пол",
    "запланируй на 20 апреля: сделать субботник",
    "Купить изюм и курагу",
    "исправить ошибку, при выводе списка дел"
]

for message in examples:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # model="gpt-4-0125-preview"
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ]
    )

    print(f" {message} -> {completion.choices[0].message.content}")
