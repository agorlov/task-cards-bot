class UserScore:
    """
    Скор пользователя
    """
    def __init__(self, user_id, db):
        self.user_id = user_id
        self.db = db

    def update_score(self, points):
        """
        Начисление очков за выполнение дела или за другие действия
        """
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE users SET karma_score = karma_score + %s WHERE telegram_id = %s",
            (points, self.user_id)
        )
        cursor.close()

    def user_score(self):
        """
        Скор пользователя
        """

        cursor = self.db.cursor()
        cursor.execute("SELECT karma_score FROM users WHERE telegram_id = %s", (self.user_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return result[0]
        else:
            return 0  # Default score if user not found