import psycopg2
from datetime import datetime


def db_connect(user_id, user_name):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))

    if not cur.fetchall():
        cur.execute("INSERT INTO users (id, date_reg, username) VALUES (%s, %s, %s)",
                    (user_id, datetime.now().date(), user_name))
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


def db_history_save(message_id, user_id, image_path, message_text,zip_path):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO req_history (id_message, id_users, message_text, message_pictures, date_mes,zip_path) VALUES (%s, %s, %s, %s, %s,%s)",
        (message_id, user_id, message_text, image_path,
         datetime.now().date(), zip_path))
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
    cur.execute(
        "SELECT message_text, message_pictures FROM req_history WHERE id_users = %s AND date_mes >= %s AND date_mes <= %s",
        (user_id, date_mes[0], date_mes[1]))
    ls = cur.fetchall()
    print(date_mes[0], date_mes[1], user_id)

    print('просмотренно')
    con.close()
    return ls


def db_favourites_update(bo, image_path):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE req_history set favourites = %s WHERE message_pictures = %s", (bo, image_path))
    con.commit()

    print('добавленно/удалено в избранное')
    con.close()


def db_favourites_view(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute(
        "SELECT message_text, message_pictures, id_message FROM req_history WHERE id_users = %s AND favourites = %s",
        (user_id, True))
    ls = cur.fetchall()

    print('просмотренно')
    con.close()
    return ls


def db_favourites_mes(id_messag, message_pictures):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE req_history set id_message = %s WHERE message_pictures = %s", (id_messag, message_pictures))
    con.commit()
    con.close()


def db_estimation(bo, message_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE req_history set estimation = %s WHERE id_message = %s", (bo, message_id))
    con.commit()
    print('like/dislike')
    con.close()


def db_message_photo(message_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT message_text, message_pictures, estimation FROM req_history WHERE id_message = %s",
                (message_id,))
    ls = cur.fetchall()
    con.close()
    return ls


def db_admin(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT admin FROM users WHERE id = %s", (user_id,))
    ls = cur.fetchall()
    con.close()
    return ls


def db_admin_activity():
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT date_mes FROM req_history")
    ls = cur.fetchall()
    con.close()
    return ls


def db_admin_users():
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT date_reg FROM users")
    ls = cur.fetchall()
    con.close()
    return ls

def db_receive_date(user_id):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="1234", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT distinct date_mes FROM req_history WHERE id_users = %s", (user_id,))
    ls = cur.fetchall()
    con.close()
    return ls


def update_zip_path(user_id,message,path):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="1234", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE req_history set zip_path = %s, message_text = %s WHERE message_pictures = %s", (path,message,user_id))
    con.commit()
    print('update zip path')
    con.close()




def db_admin_username(user_name):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("SELECT username FROM users WHERE username = %s", (user_name,))
    ls = cur.fetchall()
    con.close()
    return ls


def db_admin_coins(coins, user_name):
    con = psycopg2.connect(host="127.0.0.1", user="postgres", password="12345", database="telegramBot", port="5432")
    cur = con.cursor()
    cur.execute("UPDATE users set coins = coins + %s WHERE username = %s", (coins, user_name))
    con.commit()
    print('монеты добавлены')
    con.close()
