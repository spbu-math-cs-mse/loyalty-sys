import hashlib
import os

from dotenv import load_dotenv
from message import BotMessages


def get_bot_token():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN not found in .env file")
    return bot_token


def create_loyalty_level_message(loyalty_level):
    discount_type_name, discount_name, discount_value, _ = loyalty_level
    return (
        f"Уровень лояльности: {discount_name}"
        f"Тип скидки: {discount_type_name}\n"
        f"Значение скидки: {discount_value}\n\n"
    )


def create_info_message(total_purchases, loyalty_levels):
    enabled_message = f"Доступен следующий уровень лояльности:\n" if (len(loyalty_levels) == 1) else f"Доступны следующие уровни лояльности:\n"
    return f"{BotMessages.INFO_MESSAGE_HEADER.value}\n" +\
        f"Общая сумма покупок: {total_purchases}\n" +\
        enabled_message +\
        ''.join(create_loyalty_level_message(loyalty_levels[i]) for i in range(len(loyalty_levels)))


def generate_data_for_qr_code(user_id):
    return hashlib.sha256(f"user_id = {user_id}".encode()).hexdigest()
