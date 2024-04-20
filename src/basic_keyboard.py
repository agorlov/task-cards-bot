
from telebot import types

class BasicKeyboard:
    """
    Меню с кнопками "Взять дело", "Список дел", "Архив" (под полем ввода текста)
    """
    def __init__(self):
        pass

    def menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Взять дело")
        item2 = types.KeyboardButton("Список дел")
        item3 = types.KeyboardButton("Архив")
        markup.add(item1, item2, item3)
        return markup
