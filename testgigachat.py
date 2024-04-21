"""Пример работы с чатом через gigachain"""
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
import requests
import uuid

# Client secret
# 02be40a8-562e-4ca8-83cb-b87ae2bd4644

# Авторизационные данные
AUTH_DATA = "MjUyOTg0NmYtNGE3.....=="

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

payload='scope=GIGACHAT_API_PERS'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'application/json',
  'RqUID': str(uuid.uuid4()),
  'Authorization': f"Basic {AUTH_DATA}"
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
# в response.text находиться json-строка, мне нужен ключ access_token и expires_at
data = response.json()
access_token = data["access_token"]
expires_at = data["expires_at"]
print(f"access_token: {access_token}\nexpires_at: {expires_at}")




# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=access_token) # , verify_ssl_certs=False

# Подсчет токенов:
print("Токены для 'Сколько токенов в этой строке': ", chat.get_num_tokens("Сколько токенов в этой строке")) # chat.get_num_tokens("Сколько токенов в этой строке")

messages = [
    SystemMessage(
        content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы."
    )
]

while(True):
    user_input = input("User: ")
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    print("Bot: ", res.content)
