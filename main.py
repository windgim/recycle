import telebot
from telebot import types
import sqlite3
import random
import time

token = ""

bot = telebot.TeleBot(token)

moderator_id = 0

user_states = {}
last_video_time = {}

def ending_minutes(minutes):
    if minutes == 1:
        return "минута"

    elif 2 <= minutes % 10 <= 4:
        return "минуты"

    elif 5 <= minutes % 10 <= 9:
        return "минут"

def ending_hours(hours):
    if hours == 1:
        return "час"

    elif 2 <= hours % 10 <= 4:
        return "часа"

    elif 5 <= hours % 10 <= 9:
        return "часов"

def main():
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton(
        "Отправить видео. 📸", callback_data="video_result"
    )
    btn_info = types.InlineKeyboardButton("Инфо", callback_data="info")
    markup.add(btn_video, btn_info)
    return markup


def main_with_back():
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton(
        "Отправить видео. 📸", callback_data="video_result"
    )
    btn_back = types.InlineKeyboardButton("Назад", callback_data="back")
    markup.add(btn_video, btn_back)
    return markup


@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот, который сможет дать тебе вознаграждение за выброшенный мусор 🌍\n",
        reply_markup=main(),
    )


@bot.callback_query_handler(func=lambda call: True)
def buttons_check(call):
    if call.data == "video_result":
        user_id = call.message.chat.id
        current_time = time.time()
        last_time = last_video_time.get(user_id)

        if last_time and current_time - last_time < 86400:
            remaining_time = 86400 - (current_time - last_time)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            bot.send_message(
                user_id,
                f"Ты уже отправлял недавно видео. Подожди {hours} {ending_hours(hours)} и {minutes} {ending_minutes(minutes)}. ⌚"
            )

        else:
            user_states[user_id] = "awaiting_video"
            bot.send_message(
                user_id,
                "Отправь видео как ты утилизируешь любой мусор. 🗑️",
            )


    elif call.data == "info":
        bot.send_message(
            call.message.chat.id,
            f"""Условия получения награды: 🌱
Отправить видео в бота, с тем как вы утилизируете мусор.
После этого модерация проверит видео, и отправит вознаграждение.\n
По статистике на 2024 год, почти 48% людей признаются, что бросают мусор.
Именно по этой причине мы хотим внести свой вклад в освобождении мира от мусора на улицах.
Бот созданный нашей командой даёт мотивацию людям, выбрасывать мусор именно в отведённые для этого места.
Мотивация заключается в поощрении людей промокодами на разные сервисы, за видеодоказательство выброшенного мусора в мусорку. 🎇\n
Всего 4 основных вида мусора ♻️:
1. Пластик можно сдать в ближайший пункт переработки или использовать повторно.
2. Стекло можно сдать в пункты приёма стеклотары или выбросить в специальные контейнеры.
3. Металл перерабатывается в пунктах приёма. Не забудь очистить металл от загрязнений перед сдачей!
4. Бумагу можно переработать. Лучше всего сдать макулатуру в специальные приёмные пункты.
            """,
            reply_markup=main_with_back(),
        )

    elif call.data == "back":
        bot.send_message(
            call.message.chat.id, "Возвращаю в главное меню! ✨", reply_markup=main()
        )

    elif call.data.startswith("moderation:"):
        data = call.data.split(":")
        action = data[1]
        sender_id = int(data[2])

        db = sqlite3.connect("promo_codes.db")
        cur = db.cursor()

        promo_services = ['Wildberries', 'Ozon', 'DodoPizza', 'BurgerKing', "McDonald's"]
        random_service = random.choice(promo_services)

        cur.execute("SELECT code FROM promo_codes")
        codes = cur.fetchall()

        if codes:
            random_code = random.choice(codes)[0]
            cur.execute("DELETE FROM promo_codes WHERE code = ?", (random_code,))
            db.commit()

        else:
            bot.send_message(sender_id, "Извини, промокоды закончились 😢", reply_markup=main())

        cur.close()
        db.close()


        if action == "accept":
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(sender_id, f"Поздравляем! Вы правильно утилизировали мусор. Вот ваш промокод на {random_service}: {random_code} 🌱")
            bot.send_message(
                sender_id,
                "Привет! Я бот, который сможет дать тебе вознаграждение за выброшенный мусор 🌍\n",
                reply_markup=main(),
            )

        elif action == "reject":
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(sender_id, "К сожалению, вы неправильно утилизировали мусор. ❌")
            bot.send_message(
                sender_id,
                "Привет! Я бот, который сможет дать тебе вознаграждение за выброшенный мусор 🌍\n",
                reply_markup=main(),
            )

@bot.message_handler(content_types=["video"])
def handle_video(message):
    username = message.from_user.username
    user_id = message.from_user.id

    if user_states.get(message.chat.id) == "awaiting_video":
        bot.send_message(
            user_id,
            "Спасибо за видео! Ты молодец, что выбрасываешь мусор правильно, видео отправлено на модерацию. 🎉",
        )
        bot.send_message(
            user_id,
            "После модерации, мы свяжемся с вами для вручения подарка. 🌱",
        )
        bot.send_message(
            user_id,
            "Привет! Я бот, который сможет дать тебе вознаграждение за выброшенный мусор 🌍\n",
            reply_markup=main(),
        )

        markup = types.InlineKeyboardMarkup()
        btn_accept = types.InlineKeyboardButton("✅", callback_data=f"moderation:accept:{user_id}")
        btn_reject = types.InlineKeyboardButton("❌", callback_data=f"moderation:reject:{user_id}")
        markup.add(btn_accept, btn_reject)

        bot.forward_message(moderator_id, message.chat.id, message.message_id)
        bot.send_message(moderator_id, f"Видео от пользователя @{username}", reply_markup=markup)

        user_states[user_id] = None
        last_video_time[user_id] = time.time()

    else:
        bot.send_message(
            message.chat.id, "Нажми 'Отправить видео на проверку', чтобы загрузить видео."
        )
        bot.send_message(
            message.chat.id,
            "Привет! Я бот, который сможет дать тебе вознаграждение за выброшенный мусор 🌍\n",
            reply_markup=main(),
        )

bot.polling(none_stop=True)
