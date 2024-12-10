from enum import Enum

class Gender(Enum):
    MAN = "мужской"
    WOMAN = "женский"
    UNDEFINED = "не указано"

class DiscountType(Enum):
    POINTS = "points"
    SALE = "sale"