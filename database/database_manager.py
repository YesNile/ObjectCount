import psycopg2
from datetime import datetime


class Database:
    def __init__(self):
        self.cur = None

    def db_connect(self, user_id):
        with psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="12345",
            database="telegramBot",
            port="5432",
        ) as con:
            self.cur = con.cursor()

            self.cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not self.cur.fetchall():
                self.cur.execute(
                    "INSERT INTO users (id, date_reg, coins) VALUES (%s, %s, 10)",
                    (user_id, datetime.now().date()),
                )
                con.commit()

            print("Record inserted successfully")

    def __del__(self):
        if self.cur:
            self.cur.close()

    def db_coins(self, user_id):
        self.cur.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
        user = self.cur.fetchall()
        for coin in user:
            if coin[0] != 0:
                self.cur.execute(
                    "UPDATE users set coins = %s WHERE id = %s", (coin[0] - 1, user_id)
                )
                self.cur.commit()
                return True
            else:
                return False

    def db_score(self, user_id):
        self.cur.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
        user = self.cur.fetchall()
        for coin in user:
            return coin[0]

    def db_history_save(self, message_id, user_id, image_path, message_text):
        self.cur.execute(
            "INSERT INTO req_history (id_message, id_users, message_text, message_pictures, date_mes) VALUES (%s, %s, %s, %s, %s)",
            (message_id, user_id, message_text, image_path, datetime.now().date()),
        )
        self.con.commit()

        print("добавлено в историю")

    def db_history_allview(self, user_id):
        self.cur.execute(
            "SELECT message_text, message_pictures FROM req_history WHERE id_users = %s",
            (user_id,),
        )
        ls = self.cur.fetchall()

        print("просмотрено")
        return ls

    def db_history_view(self, user_id, date_mes):
        self.cur.execute(
            "SELECT message_text, message_pictures FROM req_history WHERE id_users = %s AND date_mes >= %s AND date_mes <= %s",
            (user_id, date_mes[0], date_mes[1]),
        )
        ls = self.cur.fetchall()
        print(date_mes[0], date_mes[1], user_id)

        print("просмотрено")
        return ls

    def db_favourites_update(self, bo, image_path):
        self.cur.execute(
            "UPDATE req_history set favourites = %s WHERE message_pictures = %s",
            (bo, image_path),
        )
        self.con.commit()

        print("добавлено/удалено в избранное")

    def db_favourites_view(self, user_id):
        self.cur.execute(
            "SELECT message_text, message_pictures FROM req_history WHERE id_users = %s AND favourites = %s",
            (user_id, True),
        )
        ls = self.cur.fetchall()

        print("просмотрено")
        return ls

    def db_estimation(self, message_id):
        self.cur.execute(
            "UPDATE req_history set estimation = %s WHERE id_message = %s",
            (False, message_id),
        )
        self.con.commit()
        print("dislike")

    def db_message_photo(self, message_id):
        self.cur.execute(
            "SELECT message_text, message_pictures FROM req_history WHERE id_message = %s",
            (message_id,),
        )
        ls = self.cur.fetchall()
        return ls
