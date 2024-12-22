from enum import Enum
from gender import Genders


class BotMessages(Enum):
    START_MESSAGE = (
        "Привет! Я бот для управления скидками. Введите /info для получения информации."
    )
    ERROR_MESSAGE = "Произошла ошибка. Попробуйте позже."
    GENDER_QUESTION = "Укажите ваш пол:"
    GENDER_UPDATED = "Пол успешно обновлен."
    INVALID_GENDER = "Неверный формат гендера."
    INFO_MESSAGE_HEADER = "Информация о вашей скидке:"
    REGISTRATION_ERROR = "Ошибка регистрации пользователя:"
    USER_ID_ERROR = "Ошибка получения user_id:"
    BACKEND_ERROR = "Ошибка взаимодействия с бэкендом:"
    BIRTHDAY_YEAR_RANGE_CHOICE = "Выберите диапазон годов рождения:"
    BIRTHDAY_YEAR_CHOICE = "Выберите год рождения:"
    BIRTHDAY_MONTH_CHOICE = "Выберите месяц рождения:"
    BIRTHDAY_DAY_CHOICE = "Выберите день рождения:"
    BIRTHDAY_CHOICE_RESULT = "Вы выбрали дату рождения: "
    BIRTHDAY_CHOICE_ERROR = "Ошибка обновления даты рождения:"
    LOYALTY_LEVEL_INCREASING = "Поздравляем! Ваш уровень лояльности повышен до"
    NEW_EVENT = "Новое событие:"
