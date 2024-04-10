
class AddedUser:
    """
    Добавленный новый пользователь в базу данных
    """

    def __init__(self, user, db):
        self.user = user
        self.db = db


    def add_user(self):
        """
        Добавить пользователя

        структуру user берем из message.from_user библиотеке telebot,
        включает поля:
            user.id, user.name, user.first_name, user.last_name
        """
        
        cursor = self.db.cursor()
        user = self.user

        # Проверка, существует ли пользователь в базе данных
        cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (user.id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Добавление нового пользователя
            cursor.execute(
                "INSERT INTO users (telegram_id, username, firstname, lastname) VALUES (%s, %s, %s, %s)",
                (user.id, user.username, user.first_name, user.last_name))
        else:
            # Обновление информации и lastmessage_time для существующего пользователя
            cursor.execute("UPDATE users SET lastmessage = NOW() WHERE telegram_id = %s", (user.id,))

        cursor.close()