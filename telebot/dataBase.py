import telebot
import psycopg2
from datetime import datetime


def db_connect(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))

    if not cur.fetchall():
        cur.execute("INSERT INTO users (id, date_reg, coins) VALUES (%s, %s, 10)", (user_id, datetime.now().date()))
        con.commit()

    print("Record inserted successfully")
    con.close()


def db_coins(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
    user = cur.fetchall()
    for coin in user:
        if coin[0] != 0:
            cur.execute("UPDATE users set coins = %s WHERE id = %s", (coin[0] - 1, user_id))
            con.commit()
            return True
        else:
            return False
    con.close()


def db_score(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
    user = cur.fetchall()
    for coin in user:
        return coin[0]
    con.close()


def db_history_save(message_id, user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO req_history (id_message, id_users, message_text, message_pictures, date_mes) VALUES (%s, %s, %s, %s, %s)",
        (message_id, user_id, 'красивое', r'C:\Users\Вероника\Desktop\Балуюсь\bot.jpg',
         datetime.now().date()))
    con.commit()

    print('добавленно в историю')
    con.close()


def db_history_allview(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT message_text, message_pictures FROM req_history WHERE id_users = %s", (user_id,))
    ls = cur.fetchall()

    print('просмотренно')
    con.close()
    return ls


def db_history_view(user_id, date_mes):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT message_text, message_pictures FROM req_history WHERE id_users = %s AND date_mes >= %s AND date_mes <= %s",
                (user_id, date_mes[0], date_mes[1]))
    ls = cur.fetchall()
    print(date_mes[0], date_mes[1], user_id)

    print('просмотренно')
    con.close()
    return ls


def db_favourites_update(message_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE req_history set favourites = %s WHERE id_message = %s", (True, message_id))
    con.commit()

    print('добавленно/удалено в избранное')
    con.close()


def db_favourites_view(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT message_text, message_pictures FROM req_history WHERE id_users = %s AND favourites = %s",
                (user_id, True))
    ls = cur.fetchall()

    print('просмотренно')
    con.close()
    return ls


def db_estimation(message_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE req_history set estimation = %s WHERE id_message = %s", (False, message_id))
    con.commit()

    print('dislike')
    con.close()
