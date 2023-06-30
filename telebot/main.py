import telebot
from telebot import types
from dataBase import db_connect, db_coins, db_score

TOKEN = '6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    db_connect(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Перейти на сайт')
    item2 = types.KeyboardButton('Получить инструкцию')
    item4 = types.KeyboardButton('Посмотреть счет')
    item3 = types.KeyboardButton('Посмотреть историю')
    markup.row(item1, item2)
    markup.row(item3, item4)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}'.format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Перейти на сайт':
            markup = types.InlineKeyboardMarkup()
            markup.add( types.InlineKeyboardButton('Перейти на сайт', url='https://www.google.ru/'))
            bot.reply_to(message, 'Нажмите, для перехода на сайт', reply_markup=markup)
        elif message.text == 'Получить инструкцию':
            bot.send_message(message.chat.id, 'Для удовлетворительного результата нужна фотография в хорошем качестве, на контрастном для объектов фоне, желательно снимать близко к объектам')
        elif message.text == 'Посмотреть счет':
            coin = db_score(message.from_user.id)
            bot.send_message(message.chat.id, f'На вашем счете: {coin} монет')
        elif message.text == 'Посмотреть историю':
            bot.send_message(message.chat.id, 'Ваша история:')


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    if db_coins(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton('Скачать архив .zip', callback_data='save')
        item2 = types.InlineKeyboardButton('👍', callback_data='like')
        item3 = types.InlineKeyboardButton('👎', callback_data='dislike')
        markup.row(item2, item3)
        markup.add(item1)
        bot.reply_to(message, 'красивое', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Упс! Ваш лимит закончился. Обатитесь к администратору для пополнения счета.')



@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    markup = types.InlineKeyboardMarkup()
    if callback.message:
        if callback.data == 'like':
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            markup.add(types.InlineKeyboardButton('Скачать архив .zip', callback_data='save'))
            bot.send_message(callback.message.chat.id, 'красивое', reply_markup=markup)
        elif callback.data == 'dislike':
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            markup.add(types.InlineKeyboardButton('Скачать архив .zip', callback_data='save'))
            bot.send_message(callback.message.chat.id, 'красивое', reply_markup=markup)
        elif callback.data == 'save':
            bot.delete_message(callback.message.chat.id, callback.message.message_id)


bot.polling(none_stop=True)