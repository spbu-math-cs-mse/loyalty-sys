import telebot
import calendar
from enum import Enum


class State(Enum):
    STATE_YEAR_RANGE = 1
    STATE_YEAR = 2
    STATE_MONTH = 3
    STATE_DAY = 4
    STATE_DONE = 5


class BirthdayCallbackStrings(Enum):
    YEAR_RANGE = "year_range:"
    YEAR = "year:"
    MONTH = "month:"
    DAY = "day:"


user_data = {}


def create_year_range_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    ranges = [(1900 + i * 10, 1900 + (i + 1) * 10 - 1) for i in range(12)]
    for start, end in ranges:
        markup.add(
            telebot.types.InlineKeyboardButton(
                text=f"{start}-{end}",
                callback_data=f"{BirthdayCallbackStrings.YEAR_RANGE.value}{start}:{end}",
            )
        )
    return markup


def create_year_keyboard(start_year, end_year):
    markup = telebot.types.InlineKeyboardMarkup(row_width=5)
    years = range(start_year, end_year + 1)
    for i in range(0, len(years), 5):
        markup.add(
            *[
                telebot.types.InlineKeyboardButton(
                    text=str(y),
                    callback_data=f"{BirthdayCallbackStrings.YEAR.value}{y}",
                )
                for y in years[i : i + 5]
            ]
        )
    return markup


def create_month_keyboard(year):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    months = range(1, 13)
    for i in range(0, len(months), 3):
        markup.add(
            *[
                telebot.types.InlineKeyboardButton(
                    text=calendar.month_name[m],
                    callback_data=f"{BirthdayCallbackStrings.MONTH.value}{year}:{m}",
                )
                for m in months[i : i + 3]
            ]
        )
    return markup


def create_day_keyboard(year, month):
    markup = telebot.types.InlineKeyboardMarkup(row_width=7)
    number_of_days = calendar.monthrange(year, month)[1]
    days = range(1, number_of_days + 1)
    for i in range(0, len(days), 7):
        markup.add(
            *[
                telebot.types.InlineKeyboardButton(
                    text=str(d),
                    callback_data=f"{BirthdayCallbackStrings.DAY.value}{year}:{month}:{d}",
                )
                for d in days[i : i + 7]
            ]
        )
    return markup
