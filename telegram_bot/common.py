from message import BotMessages
from dotenv import load_dotenv

import os
import hashlib


def get_bot_token():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN not found in .env file")
    return bot_token


def create_info_message(discount_info, total_purchases, loyalty_level):
    return (
        f"{BotMessages.INFO_MESSAGE_HEADER.value}\n"
        f"Тип скидки: {discount_info['type']}\n"
        f"Значение скидки: {discount_info['value']}\n"
        f"Общая сумма покупок: {total_purchases}\n"
        f"Уровень лояльности: {loyalty_level}"
    )


def generate_data_for_qr_code(user_id):
    return hashlib.sha256(f"user_id = {user_id}".encode()).hexdigest()
