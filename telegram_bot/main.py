from io import BytesIO
from PIL import Image

from common import get_bot_token, create_info_message, generate_data_for_qr_code
from message import BotMessages
from gender import Genders
from telebot import types
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

import telebot
import requests
import qrcode

BOT_TOKEN = get_bot_token()
BACKEND_URL = "http://84.201.143.213:5000"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message):
    markup = create_default_buttons()
    bot.send_message(
        message.chat.id, BotMessages.START_MESSAGE.value, reply_markup=markup
    )
    register_user(message.chat.id)


@bot.message_handler(commands=["info"])
def send_info(message):
    try:
        user_id = get_user_id(message.chat.id)
        discount_info = get_discount_info(user_id)
        total_purchases = get_total_purchases(user_id)
        loyalty_level = get_loyalty_level(user_id)

        if (total_purchases < 5000):
            loyalty_level = "Бронзовый"
            discount_info = {"type": "Скидка", "value": 5}
        elif (total_purchases >= 5000 and total_purchases < 50000):
            loyalty_level = "Серебряный"
            discount_info = {"type": "Скидка", "value": 15}
        else:
            loyalty_level = "Золотой"
            discount_info = {"type": "Скидка", "value": 25}

        info_message = create_info_message(
            discount_info, total_purchases, loyalty_level
        )
        bot.send_message(message.chat.id, info_message)
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"{BotMessages.BACKEND_ERROR.value} ({e})")
    except Exception as e:
        bot.send_message(message.chat.id, f"{BotMessages.ERROR_MESSAGE.value} ({e})")


@bot.message_handler(commands=["qrcode"])
def send_qrcode(message):
    try:
        user_id = get_user_id(message.chat.id)
        # TODO: think about saving this, not regenerating
        qr_code = generate_qr_code(user_id)
        bot.send_photo(message.chat.id, qr_code)
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"{BotMessages.BACKEND_ERROR.value} ({e})")
    except Exception as e:
        bot.send_message(message.chat.id, f"{BotMessages.ERROR_MESSAGE.value} ({e})")


@bot.message_handler(commands=["gender"])
def ask_gender(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(Genders.MALE.value, Genders.FEMALE.value, Genders.NOT_STATED.value)
    bot.send_message(
        message.chat.id, BotMessages.GENDER_QUESTION.value, reply_markup=markup
    )
    bot.register_next_step_handler(message, process_gender)


def create_default_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/info", "/qrcode", "/gender")
    return markup


def process_gender(message):
    gender = message.text.lower()
    if gender in [g.value for g in Genders]:
        try:
            update_gender(message.chat.id, gender)
            markup = create_default_buttons()
            bot.send_message(
                message.chat.id, BotMessages.GENDER_UPDATED.value, reply_markup=markup
            )
        except requests.exceptions.RequestException as e:
            bot.send_message(
                message.chat.id, f"{BotMessages.BACKEND_ERROR.value} ({e})"
            )

        except Exception as e:
            bot.send_message(
                message.chat.id, f"{BotMessages.ERROR_MESSAGE.value} ({e})"
            )
    else:
        bot.send_message(message.chat.id, BotMessages.INVALID_GENDER.value)


def register_user(chat_id):
    response = requests.post(f"{BACKEND_URL}/user", json={"chat_id": str(chat_id)})
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(f"{BotMessages.REGISTRATION_ERROR.value} {response.text}")


def get_user_id(chat_id):
    response = requests.post(f"{BACKEND_URL}/user", json={"chat_id": str(chat_id)})
    if response.status_code == 200 or response.status_code == 201:
        return response.json()["user_id"]
    else:
        raise Exception(f"{BotMessages.USER_ID_ERROR.value} {response.text}")


def get_discount_info(user_id):
    response = requests.get(f"{BACKEND_URL}/user/{user_id}/discount")
    response.raise_for_status()
    return response.json()


def get_total_purchases(user_id):
    response = requests.get(f"{BACKEND_URL}/user/{user_id}/total_purchases")
    response.raise_for_status()
    return response.json()["total_purchases"]


def get_loyalty_level(user_id):
    response = requests.get(f"{BACKEND_URL}/user/{user_id}/loyalty_level")
    response.raise_for_status()
    return response.json()["loyalty_level"]


def update_gender(chat_id, gender):
    user_id = get_user_id(chat_id)
    response = requests.put(
        f"{BACKEND_URL}/user/{user_id}/gender", json={"gender": gender}
    )
    response.raise_for_status()


def generate_qr_code(user_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(generate_data_for_qr_code(user_id))
    qr.make(fit=True)
    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
    )
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


if __name__ == "__main__":
    bot.infinity_polling()
