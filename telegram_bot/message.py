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
