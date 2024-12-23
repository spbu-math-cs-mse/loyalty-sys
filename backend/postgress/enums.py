from enum import Enum

class Gender(Enum):
    MAN = "мужской"
    WOMAN = "женский"
    UNDEFINED = "не указано"

class DiscountType(Enum):
    SALE = "sale"
    POINTS = "points"