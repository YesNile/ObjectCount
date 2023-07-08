import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from ultralytics import YOLO

from database import database_manager as dataBase
from ml.process_image import SegmentationModule

TOKEN = "6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw"
bot = telebot.TeleBot(TOKEN)

model = SegmentationModule(r"../best_with_badges.pt")

user_id = 0
res = []
fav = []

@bot.message_handler(commands=['start'])
def start(message):
    dataBase.db_connect(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('Перейти на сайт')
    item2 = types.KeyboardButton('Получить инструкцию')
    item3 = types.KeyboardButton('Посмотреть счет')
    item4 = types.KeyboardButton('Посмотреть историю')
    item5 = types.KeyboardButton('Посмотреть избранное')
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}!\n Загрузи фотографию с объектами, которые обычно лежат '
                                      'на твоем столе, и узнай сколько предметов одной категории на ней '
                                      'присутствует'.format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    global user_id
    if message.chat.type == 'private':
        if message.text == 'Перейти на сайт':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://www.google.ru/'))
            bot.reply_to(message, 'Нажмите, для перехода на сайт', reply_markup=markup)

        elif message.text == 'Получить инструкцию':
            bot.send_message(message.chat.id,
                             'Я обучен распознаванию порядка 25 различных объектов. Для удовлетворительного '
                             'результата нужна фотография в хорошем качестве, на контрастном для объектов фоне, '
                             'желательно снимать близко к объектам')

        elif message.text == 'Посмотреть счет':
            coin = dataBase.db_score(message.from_user.id)
            bot.send_message(message.chat.id, f'На вашем счете: {coin} монет')

        elif message.text == 'Посмотреть историю':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            item1 = types.KeyboardButton('За все время')
            item2 = types.KeyboardButton('Ввести самостоятельно')
            item3 = types.KeyboardButton('Назад')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, f'Выберете период: ', reply_markup=markup)

        elif message.text == 'Посмотреть избранное':
            fav.clear()
            user_id = message.from_user.id

            history = dataBase.db_favourites_view(message.from_user.id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Скачать архив .zip', callback_data='save'))
            markup.add(types.InlineKeyboardButton('Удалить из избранного', callback_data='delete'))
            for mes in history:
                photo_lsd = open(mes[1], 'rb')
                fav_mes = bot.send_photo(message.chat.id, photo_lsd, mes[0], reply_markup=markup)
                fav.append(fav_mes.message_id)

        elif message.text == 'Назад':
            dataBase.db_connect(message.from_user.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            item1 = types.KeyboardButton('Перейти на сайт')
            item2 = types.KeyboardButton('Получить инструкцию')
            item3 = types.KeyboardButton('Посмотреть счет')
            item4 = types.KeyboardButton('Посмотреть историю')
            item5 = types.KeyboardButton('Посмотреть избранное')
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

        with open(image_path, 'wb') as file:
            file.write(downloaded_file)
        segmented_images = model.segment_image(image_path, model, photo_id)

        photo_lsd = open(image_path, 'rb')
        msg = bot.send_photo(message.chat.id, photo_lsd, f"Количество найденных объектов на фотографии: {len(segmented_images)}", reply_markup=markup)
        dataBase.db_history_save(msg.id, message.from_user.id, image_path, f"Количество найденных объектов на фотографии: {len(segmented_images)}")
    else:
        markup.add(types.InlineKeyboardButton('Написать администратору', url='https://t.me/Jiraffeck'))
        bot.send_message(message.chat.id, 'Упс! Ваш лимит закончился. Обратитесь к администратору для пополнения счета.',
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global user_id
    image = dataBase.db_message_photo(callback.message.message_id)
    if callback.message:
        if callback.data == 'save':
            if image:
                file = open(fr"{image[0][1].split('.')[0]}.zip", 'rb')
            else:
                history = dataBase.db_favourites_view(user_id)
                i = fav.index(callback.message.message_id)
                file = open(fr"{history[i][1].split('.')[0]}.zip", 'rb')
            bot.send_document(callback.message.chat.id, file)

        elif callback.data == 'favourites':
            dataBase.db_favourites_update(True, image[0][1])
            bot.send_message(callback.message.chat.id, 'Добавленно в избранное.')

        elif callback.data == 'delete':
            history = dataBase.db_favourites_view(user_id)
            i = fav.index(callback.message.message_id)
            fav.remove(fav[i])
            dataBase.db_favourites_update(False, history[i][1])
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, 'Удалено из избранного.')

        if image:
            if image[0][2] is None:
                if callback.data == 'like':
                    dataBase.db_estimation(True, callback.message.message_id)
                    bot.send_message(callback.message.chat.id, 'Спасибо за ваш голос!')

                elif callback.data == 'dislike':
                    dataBase.db_estimation(False, callback.message.message_id)
                    bot.send_message(callback.message.chat.id, 'Спасибо за ваш голос! Мы обязательно исправим все недочеты в будущем!')




bot.polling(none_stop=True)