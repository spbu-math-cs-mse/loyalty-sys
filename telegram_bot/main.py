from io import BytesIO
from PIL import Image
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request

from common import get_bot_token, create_info_message, generate_data_for_qr_code
from birthday_utils import (
    user_data,
    State,
    BirthdayCallbackStrings,
    create_year_range_keyboard,
    create_year_keyboard,
    create_month_keyboard,
    create_day_keyboard,
)
from message import BotMessages
from gender import Genders
from telebot import types
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

import telebot
import requests
import qrcode
import uvicorn
import threading

BOT_TOKEN = get_bot_token()
BACKEND_URL = "http://84.201.143.213:5000"

bot = telebot.TeleBot(BOT_TOKEN)
app = FastAPI()


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
        total_purchases = get_total_purchases(user_id)
        loyalty_levels = get_loyalty_levels(user_id)

        info_message = create_info_message(total_purchases, loyalty_levels)

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


@bot.message_handler(commands=["birthday"])
def ask_birthday(message):
    user_data[message.chat.id] = {"state": State.STATE_YEAR_RANGE.value}
    markup = create_year_range_keyboard()
    bot.send_message(
        message.chat.id,
        BotMessages.BIRTHDAY_YEAR_RANGE_CHOICE.value,
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(BirthdayCallbackStrings.YEAR_RANGE.value)
)
def process_year_range(call):
    start_year, end_year = map(
        int, call.data[len(BirthdayCallbackStrings.YEAR_RANGE.value) :].split(":")
    )
    user_data[call.from_user.id]["state"] = State.STATE_YEAR.value
    markup = create_year_keyboard(start_year, end_year)
    bot.edit_message_text(
        text=BotMessages.BIRTHDAY_YEAR_CHOICE.value,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(BirthdayCallbackStrings.YEAR.value)
)
def process_year(call):
    year = int(call.data[len(BirthdayCallbackStrings.YEAR.value) :])
    user_data[call.from_user.id]["state"] = State.STATE_MONTH.value
    user_data[call.from_user.id]["year"] = year
    markup = create_month_keyboard(year)
    bot.edit_message_text(
        text=BotMessages.BIRTHDAY_MONTH_CHOICE.value,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(BirthdayCallbackStrings.MONTH.value)
)
def process_month(call):
    year, month = map(
        int, call.data[len(BirthdayCallbackStrings.MONTH.value) :].split(":")
    )
    user_data[call.from_user.id]["state"] = State.STATE_DAY.value
    user_data[call.from_user.id]["month"] = month
    markup = create_day_keyboard(year, month)
    bot.edit_message_text(
        text=BotMessages.BIRTHDAY_DAY_CHOICE.value,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(BirthdayCallbackStrings.DAY.value)
)
def process_day(call):
    year, month, day = map(
        int, call.data[len(BirthdayCallbackStrings.DAY.value) :].split(":")
    )
    birthday = datetime(year, month, day)
    user_data[call.from_user.id]["state"] = State.STATE_DONE.value
    user_data[call.from_user.id]["birthday"] = birthday
    bot.edit_message_text(
        text=f"{BotMessages.BIRTHDAY_CHOICE_RESULT.value}{birthday.strftime('%Y-%m-%d')}",
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )
    try:
        update_birthday(call.from_user.id, birthday)
    except Exception as e:
        bot.send_message(
            call.message.chat.id, f"{BotMessages.BIRTHDAY_CHOICE_ERROR.value} {e}"
        )


def create_default_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("/info", "/qrcode", "/gender", "/birthday")
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


def get_total_purchases(user_id):
    response = requests.get(f"{BACKEND_URL}/user/{user_id}/total_purchases")
    response.raise_for_status()
    return response.json()["total_purchases"]


def get_loyalty_levels(user_id):
    response = requests.get(f"{BACKEND_URL}/user/{user_id}/loyalty_level")
    response.raise_for_status()
    return response.json()["loyalty_level"]


def update_gender(chat_id, gender):
    user_id = get_user_id(chat_id)
    response = requests.put(
        f"{BACKEND_URL}/user/{user_id}/gender", json={"gender": gender}
    )
    response.raise_for_status()


def update_birthday(chat_id, birthday):
    user_id = 1
    response = requests.put(
        f"{BACKEND_URL}/user/{user_id}/birthday",
        json={"birthday": birthday.strftime("%Y-%m-%d")},
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


@app.post("/loyalty_updates/")
async def loyalty_update(request: Request):
    try:
        data = await request.json()
        chat_id = data["chat_id"]
        loyalty_level = data["loyalty_level"]
        send_loyalty_update_message(chat_id, loyalty_level)
        return {"status": "success"}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"{BotMessages.BACKEND_ERROR.value} {e}"
        )


@app.post("/new_event/")
async def loyalty_update(request: Request):
    try:
        data = await request.json()
        chat_id = data["chat_id"]
        name = data["name"]
        description = data["description"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        send_new_event_message(chat_id, name, description, start_date, end_date)
        return {"status": "success"}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"{BotMessages.BACKEND_ERROR.value} {e}"
        )


def send_loyalty_update_message(chat_id, loyalty_level):
    try:
        message = f"{BotMessages.LOYALTY_LEVEL_INCREASING.value} {loyalty_level[0]} (Тип: {loyalty_level[2]})\nТеперь значение вашей скидки составляет {loyalty_level[1]}%!"
        bot.send_message(chat_id, message)
    except Exception as e:
        print(f"{BotMessages.BACKEND_ERROR.value} {e}")


def send_new_event_message(chat_id, name, description, start_date, end_date):
    try:
        print(chat_id)
        message = f"{BotMessages.NEW_EVENT.value} {name} ({start_date}-{end_date})!\n\n{description}"
        print(message)
        bot.send_message(chat_id, message)
    except Exception as e:
        print(f"{BotMessages.BACKEND_ERROR.value} {e}")


if __name__ == "__main__":
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=5050)).start()
    bot.infinity_polling()
