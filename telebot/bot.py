import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from collections import Counter
import matplotlib.pyplot as plt
import random
from ultralytics import YOLO
from os import path


from database import database_manager as dataBase
from ml.process_image import SegmentationModule

TOKEN = "6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw"
bot = telebot.TeleBot(TOKEN)

model = SegmentationModule(r"../best_with_badges.pt")

user_id = 0
res = []


@bot.message_handler(commands=['start'])
def start(message):
    dataBase.db_connect(message.from_user.id, message.from_user.full_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('Сайт')
    item2 = types.KeyboardButton('Инструкция')
    item3 = types.KeyboardButton('Баланс')
    item4 = types.KeyboardButton('История')
    item5 = types.KeyboardButton('Избранное')
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}!\nГотов узнать больше о предметах на твоем столе? '
                                      'Просто сделай фото и отправь мне, а я скажу, сколько предметов и какой '
                                      'категории они принадлежат.'.format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['admin'])
def start(message):
    if dataBase.db_admin(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton('Пополнить баланс')
        item2 = types.KeyboardButton('Посмотреть активность')
        item3 = types.KeyboardButton('Посмотреть статистику пользователей')
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, 'Привет админ! Что привело тебя сюда?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'В доступе отказано')


@bot.message_handler(content_types=['text'])
def bot_message(message):
    global user_id
    if message.chat.type == 'private':
        if message.text == 'Сайт':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://www.google.ru/'))
            bot.reply_to(message, 'Нажмите, для перехода на сайт', reply_markup=markup)

        elif message.text == 'Инструкция':
            bot.send_message(message.chat.id,
                             'Я обучен распознаванию порядка 25 различных объектов. Для удовлетворительного '
                             'результата нужна фотография в хорошем качестве, на контрастном для объектов фоне, '
                             'желательно снимать близко к объектам')

        elif message.text == 'Баланс':
            coin = dataBase.db_score(message.from_user.id)
            admins = ['https://t.me/Jiraffeck', 'https://t.me/nortrow', 'https://t.me/IvanGroznyiA']
            admin = random.choice(admins)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Написать администратору', url= admin))
            bot.send_message(message.chat.id, f'На вашем счете: {coin} токенов', reply_markup=markup)

        elif message.text == 'История':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            item1 = types.KeyboardButton('За все время')
            item2 = types.KeyboardButton('Ввести самостоятельно')
            item3 = types.KeyboardButton('Назад')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, f'Выберите период: ', reply_markup=markup)

        elif message.text == 'Избранное':
            user_id = message.from_user.id

            history = dataBase.db_favourites_view(message.from_user.id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Скачать архив .zip', callback_data='save'))
            markup.add(types.InlineKeyboardButton('Удалить из избранного', callback_data='delete'))
            for mes in history:
                photo_lsd = open(mes[1], 'rb')
                fav_mes = bot.send_photo(message.chat.id, photo_lsd, mes[0], reply_markup=markup)
                dataBase.db_favourites_mes(fav_mes.message_id, mes[1])

        elif message.text == 'Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            item1 = types.KeyboardButton('Сайт')
            item2 = types.KeyboardButton('Инструкция')
            item3 = types.KeyboardButton('Баланс')
            item4 = types.KeyboardButton('История')
            item5 = types.KeyboardButton('Избранное')
            markup.add(item1, item2, item3, item4, item5)
            bot.send_message(message.chat.id, 'Продолжим', reply_markup=markup)
            res.clear()

        elif message.text == 'За все время':
            history = dataBase.db_history_allview(message.from_user.id)
            bot.send_message(message.chat.id, 'Ваша история')
            for mes in history:
                photo_lsd = open(mes[1], 'rb')
                bot.send_photo(message.chat.id, photo_lsd, f'Сообщение: {mes[0]}')

        elif message.text == 'Ввести самостоятельно':
            res.clear()
            calendar, step = DetailedTelegramCalendar().build()
            bot.send_message(message.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar)
            user_id = message.from_user.id
        # ---------------------------------------------------------------------------------------------------
        elif message.text == 'Посмотреть активность':
            if dataBase.db_admin(message.from_user.id):
                dates = dataBase.db_admin_activity()
                array = Counter(dates)
                c, d, text = [], [], []
                for day in sorted(set(dates)):
                    c.append(array[day])
                    d.append(f'{day[0]}')
                fig = plt.figure()
                plt.plot(d, c)
                fig.savefig('saved_figure.png')
                photo_lsd = open('saved_figure.png', 'rb')
                bot.send_photo(message.chat.id, photo_lsd, 'Активкность ')

        elif message.text == 'Посмотреть статистику пользователей':
            if dataBase.db_admin(message.from_user.id):
                dates = dataBase.db_admin_users()
                array = Counter(dates)
                c, d, text = [], [], []
                for day in sorted(set(dates)):
                    c.append(array[day])
                    d.append(f'{day[0]}')
                fig = plt.figure()
                plt.plot(d, c)
                fig.savefig('saved_figure.png')
                photo_lsd = open('saved_figure.png', 'rb')
                bot.send_photo(message.chat.id, photo_lsd, 'Статистика ')

        elif message.text == 'Пополнить баланс':
            if dataBase.db_admin(message.from_user.id):
                mesg = bot.send_message(message.chat.id, 'Введите имя пользователя')
                bot.register_next_step_handler(mesg, test)


def test(message):
    ls = dataBase.db_admin_username(message.text)
    print(ls, ' ', message.text)
    if ls:
        mesg = bot.send_message(message.chat.id, 'Введите количесво монет')
        bot.register_next_step_handler(mesg, coin, message.text)
    else:
        bot.send_message(message.chat.id, 'Пользователя с таким именем не существует!')


def coin(message, user_name):
    if (message.text).isdigit():
        dataBase.db_admin_coins(message.text, user_name)
        bot.send_message(message.chat.id, 'Монеты добавлены')
    else:
        bot.send_message(message.chat.id, 'Введите целое число')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              c.message.chat.id,
                              c.message.message_id)
        res.append(result)
        if len(res) == 1:
            calendar, step = DetailedTelegramCalendar().build()
            bot.send_message(c.message.chat.id,
                             f"Select {LSTEP[step]}",
                             reply_markup=calendar)
    if len(res) == 2:
        history = dataBase.db_history_view(user_id, res)
        bot.send_message(c.message.chat.id, 'Ваша история')
        for mess in history:
            photo_lsd = open(mess[1], 'rb')
            bot.send_photo(c.message.chat.id, photo_lsd, f'Сообщение: {mess[0]}')
            res.clear()


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    if dataBase.db_coins(message.from_user.id):

        item1 = types.InlineKeyboardButton('Скачать архив .zip', callback_data='save')
        item2 = types.InlineKeyboardButton('👍', callback_data='like')
        item3 = types.InlineKeyboardButton('👎', callback_data='dislike')
        item4 = types.InlineKeyboardButton('Добавить в избранное', callback_data='favourites')
        markup.row(item2, item3)
        markup.add(item1)
        markup.add(item4)

        photo_id = message.photo[-1].file_id
        file_info = bot.get_file(photo_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)
        image_path = fr"../images/{photo_id}.jpg"
        zip_path = rf"../images/{photo_id}.zip"

        with open(image_path, 'wb') as file:
            file.write(downloaded_file)
        segmented_images = model.segment_image(image_path, photo_id)

        photo_lsd = open(image_path, 'rb')
        msg = bot.send_photo(message.chat.id, photo_lsd, f"Количество найденных объектов на фотографии: {len(segmented_images)}", reply_markup=markup)
        dataBase.db_history_save(msg.id, message.from_user.id, image_path, f"Количество найденных объектов на фотографии: {len(segmented_images)}", zip_path)
    else:
        markup.add(types.InlineKeyboardButton('Написать администратору', url='https://t.me/Jiraffeck'))
        bot.send_message(message.chat.id,
                         'Упс! Ваш лимит закончился. Обратитесь к администратору для пополнения счета.',
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global user_id
    image = dataBase.db_message_photo(callback.message.message_id)
    if callback.message:
        if callback.data == 'save':
            file = open(fr"{image[0][3]}", 'rb')
            bot.send_document(callback.message.chat.id, file)

        elif callback.data == 'favourites':
            dataBase.db_favourites_update(True, image[0][1])
            bot.send_message(callback.message.chat.id, 'Добавленно в избранное.')

        elif callback.data == 'delete':
            history = dataBase.db_favourites_view(user_id)
            for fav in history:
                if fav[2] == callback.message.message_id:
                    dataBase.db_favourites_update(False, fav[1])
                    bot.delete_message(callback.message.chat.id, callback.message.message_id)
                    bot.send_message(callback.message.chat.id, 'Удалено из избранного.')

        if image:
            if image[0][2] is None:
                if callback.data == 'like':
                    dataBase.db_estimation(True, callback.message.message_id)
                    bot.send_message(callback.message.chat.id, 'Спасибо за ваш голос!')

                elif callback.data == 'dislike':
                    dataBase.db_estimation(False, callback.message.message_id)
                    bot.send_message(callback.message.chat.id,
                                     'Спасибо за ваш голос! Мы обязательно исправим все недочеты в будущем!')


bot.polling(none_stop=True)
