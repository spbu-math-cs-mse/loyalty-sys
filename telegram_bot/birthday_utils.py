import telebot
import calendar
from enum import Enum


START_YEAR = 1900
YEAR_RANGE = 10
NUMBER_OF_RANGES = 12


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
    ranges = [
        (
            START_YEAR + i * YEAR_RANGE,
            START_YEAR + (i + 1) * YEAR_RANGE - 1
        ) for i in range(NUMBER_OF_RANGES)
    ]
    for start, end in ranges:
        markup.add(
            telebot.types.InlineKeyboardButton(
                text=f"{start}-{end}",
                callback_data=f"{BirthdayCallbackStrings.YEAR_RANGE.value}{start}:{end}",
            )
        )
    return markup


def create_keyboard(row_width, start_range, end_range, text_function, callback_data_prefix):
    markup = telebot.types.InlineKeyboardMarkup(row_width=row_width)
    ranges = range(start_range, end_range)
    for i in range(0, len(ranges), row_width):
        markup.add(
            *[
                telebot.types.InlineKeyboardButton(
                    text=text_function(j),
                    callback_data=f"{callback_data_prefix}{j}",
                )
                for j in ranges[i : i + row_width]
            ]
        )
    return markup


def create_year_keyboard(start_year, end_year):
    return create_keyboard(
        row_width=5,
        start_range=start_year,
        end_range=end_year + 1,
        text_function=str,
        callback_data_prefix=BirthdayCallbackStrings.YEAR.value
    )


def create_month_keyboard(year):
    return create_keyboard(
        row_width=3,
        start_range=1,
        end_range=13,
        text_function=lambda month_number : calendar.month_name[month_number],
        callback_data_prefix=f"{BirthdayCallbackStrings.MONTH.value}{year}:"
    )


def create_day_keyboard(year, month):
    _, number_of_days = calendar.monthrange(year, month)
    return create_keyboard(
        row_width=7,
        start_range=1,
        end_range=number_of_days+1,
        text_function=str,
        callback_data_prefix=f"{BirthdayCallbackStrings.DAY.value}{year}:{month}:"
    )
