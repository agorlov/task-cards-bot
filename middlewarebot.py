import telebot
import logging

class MiddlewareBot(telebot.TeleBot):
    def __init__(self, token):
        super().__init__(token)
        self._middleware_handlers = []

    def middleware_handler(self, function):
        self._middleware_handlers.append(function)

    def _execute_middleware(self, message):
        for handler in self._middleware_handlers:
            handler(message)

    def process_new_updates(self, updates):
        for update in updates:
            if update.message:
                self._execute_middleware(update.message)
            super().process_new_updates([update])

    def send_message(self, *args, **kwargs):
        logging.info(f"{args[0]} bot> {args[1]}")
        return super().send_message(*args, **kwargs)


