import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from ultralytics import YOLO

from database.database_manager import Database
from ml.process_image import SegmentationModule

TOKEN = "6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw"
database = Database()
database.db_connect("user123")

model = SegmentationModule("./best_with_badges.pt")


class Bot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.model = YOLO(r"D:\Projects_cv\ObjectCount\best.pt")
        self.user_id = 0
        self.res = []

    def start(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            database.db_connect(message.from_user.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            item1 = types.KeyboardButton("Перейти на сайт")
            item2 = types.KeyboardButton("Получить инструкцию")
            item3 = types.KeyboardButton("Посмотреть счет")
            item4 = types.KeyboardButton("Посмотреть историю")
            item5 = types.KeyboardButton("Посмотреть избранное")
            markup.add(item1, item2, item3, item4, item5)
            self.bot.send_message(
                message.chat.id,
                "Привет, {0.first_name}!\n Загрузи фотографию с объектами, которые обычно лежат "
                "на твоем столе, и узнай сколько предметов одной категории на ней "
                "присутствует".format(message.from_user),
                reply_markup=markup,
            )

        @self.bot.message_handler(content_types=["text"])
        def bot_message(message):
            if message.chat.type == "private":
                if message.text == "Перейти на сайт":
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(
                            "Перейти на сайт", url="https://www.google.ru/"
                        )
                    )
                    self.bot.reply_to(
                        message, "Нажмите, для перехода на сайт", reply_markup=markup
                    )

                elif message.text == "Получить инструкцию":
                    self.bot.send_message(
                        message.chat.id,
                        "Я обучен распознаванию порядка 25 различных объектов. Для удовлетворительного "
                        "результата нужна фотография в хорошем качестве, на контрастном для объектов фоне, "
                        "желательно снимать близко к объектам",
                    )

                elif message.text == "Посмотреть счет":
                    coin = database.db_score(message.from_user.id)
                    self.bot.send_message(
                        message.chat.id, f"На вашем счете: {coin} монет"
                    )

                elif message.text == "Посмотреть историю":
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2
                    )
                    item1 = types.KeyboardButton("За все время")
                    item2 = types.KeyboardButton("Ввести самостоятельно")
                    item3 = types.KeyboardButton("Назад")
                    markup.add(item1, item2, item3)
                    self.bot.send_message(
                        message.chat.id, f"Выберете период: ", reply_markup=markup
                    )

                elif message.text == "Посмотреть избранное":
                    history = database.db_favourites_view(message.from_user.id)
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(
                            "Удалить из избранного", callback_data="delete"
                        )
                    )

                    for mes in history:
                        photo_lsd = open(mes[1], "rb")
                        self.bot.send_photo(
                            message.chat.id, photo_lsd, mes[0], reply_markup=markup
                        )

                elif message.text == "Назад":
                    database.db_connect(message.from_user.id)
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2
                    )
                    item1 = types.KeyboardButton("Перейти на сайт")
                    item2 = types.KeyboardButton("Получить инструкцию")
                    item3 = types.KeyboardButton("Посмотреть счет")
                    item4 = types.KeyboardButton("Посмотреть историю")
                    item5 = types.KeyboardButton("Посмотреть избранное")
                    markup.add(item1, item2, item3, item4, item5)
                    self.bot.send_message(
                        message.chat.id, "Продолжим", reply_markup=markup
                    )
                    self.res.clear()

                elif message.text == "За все время":
                    history = database.db_history_allview(message.from_user.id)
                    self.bot.send_message(message.chat.id, "Ваша история")
                    for mes in history:
                        photo_lsd = open(mes[1], "rb")
                        self.bot.send_photo(
                            message.chat.id, photo_lsd, f"Сообщение: {mes[0]}"
                        )

                elif message.text == "Ввести самостоятельно":
                    self.res.clear()
                    calendar, step = DetailedTelegramCalendar().build()
                    self.bot.send_message(
                        message.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar
                    )
                    self.user_id = message.from_user.id

        @self.bot.callback_query_handler(func=DetailedTelegramCalendar.func())
        def cal(c):
            result, key, step = DetailedTelegramCalendar().process(c.data)
            if not result and key:
                self.bot.edit_message_text(
                    f"Select {LSTEP[step]}",
                    c.message.chat.id,
                    c.message.message_id,
                    reply_markup=key,
                )
            elif result:
                self.bot.edit_message_text(
                    f"You selected {result}", c.message.chat.id, c.message.message_id
                )
                self.res.append(result)
                if len(self.res) == 1:
                    calendar, step = DetailedTelegramCalendar()
                    self.bot.send_message(
                        c.message.chat.id,
                        f"Select {LSTEP[step]}",
                        reply_markup=calendar,
                    )
            if len(self.res) == 2:
                print(self.user_id)
                history = database.db_history_view(self.user_id, self.res)
                self.bot.send_message(c.message.chat.id, "Ваша история")
                for mess in history:
                    photo_lsd = open(mess[1], "rb")
                    self.bot.send_photo(
                        c.message.chat.id, photo_lsd, f"Сообщение: {mess[0]}"
                    )
                    self.res.clear()

        @self.bot.message_handler(content_types=["photo"])
        def get_photo(message):
            markup = types.InlineKeyboardMarkup()
            if database.db_coins(message.from_user.id):
                item1 = types.InlineKeyboardButton(
                    "Скачать архив .zip", callback_data="save"
                )
                item2 = types.InlineKeyboardButton("👍", callback_data="like")
                item3 = types.InlineKeyboardButton("👎", callback_data="dislike")
                item4 = types.InlineKeyboardButton(
                    "Добавить в избранное", callback_data="favourites"
                )
                markup.row(item2, item3)
                markup.add(item1)
                markup.add(item4)

                photo_id = message.photo[-1].file_id
                file_info = self.bot.get_file(photo_id)
                file_path = file_info.file_path
                downloaded_file = self.bot.download_file(file_path)
                image_path = rf"D:\Projects_cv\ObjectCount\images\{photo_id}.jpg"

                with open(image_path, "wb") as file:
                    file.write(downloaded_file)
                segmented_images = model.segment_image(image_path, self.model, photo_id)

                # for segmented_image in segmented_images:
                #     with open(segmented_image, 'rb') as photo:
                # msg = self.bot.send_document(message.chat.id, photo, reply_markup=markup)
                photo_lsd = open(image_path, "rb")
                msg = self.bot.send_photo(
                    message.chat.id,
                    photo_lsd,
                    f"Количество найденных объектов на фотографии: {len(segmented_images)}",
                    reply_markup=markup,
                )
                database.db_history_save(
                    msg.id,
                    message.from_user.id,
                    image_path,
                    f"Количество найденных объектов на фотографии: {len(segmented_images)}",
                )
            else:
                markup.add(
                    types.InlineKeyboardButton(
                        "Написать администратору", url="https://t.me/Jiraffeck"
                    )
                )
                self.bot.send_message(
                    message.chat.id,
                    "Упс! Ваш лимит закончился. Обратитесь к администратору для пополнения счета.",
                    reply_markup=markup,
                )

        @self.bot.callback_query_handler(func=lambda callback: True)
        def callback_message(callback):
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("Скачать архив .zip", callback_data="save")
            )
            markup.add(
                types.InlineKeyboardButton(
                    "Добавить в избранное", callback_data="favourites"
                )
            )
            image = database.db_message_photo(callback.message.message_id)
            photo_lsd = open(image[0][1], "rb")

            if callback.message:
                if callback.data == "like":
                    self.bot.delete_message(
                        callback.message.chat.id, callback.message.message_id
                    )
                    self.bot.send_photo(
                        callback.message.chat.id,
                        photo_lsd,
                        image[0][0],
                        reply_markup=markup,
                    )

                elif callback.data == "dislike":
                    database.db_estimation(callback.message.message_id)
                    self.bot.delete_message(
                        callback.message.chat.id, callback.message.message_id
                    )
                    self.bot.send_photo(
                        callback.message.chat.id,
                        photo_lsd,
                        image[0][0],
                        reply_markup=markup,
                    )

                elif callback.data == "save":
                    file = open(
                        rf"{image[0][1].split('.')[0]}.zip", "rb"
                    )  # надо будет менять
                    self.bot.send_document(callback.message.chat.id, file)

                elif callback.data == "favourites":
                    database.db_favourites_update(True, image[0][1])
                    self.bot.send_message(
                        callback.message.chat.id, "Добавлено в избранное."
                    )

                elif callback.data == "delete":
                    # database.db_favourites_update(False, callback.message.)
                    self.bot.delete_message(
                        callback.message.chat.id, callback.message.message_id
                    )
                    self.bot.send_message(
                        callback.message.chat.id, "Удалено из избранного."
                    )

        self.bot.polling(none_stop=True)


if __name__ == "__main__":
    bot = Bot(TOKEN)
    bot.start()
