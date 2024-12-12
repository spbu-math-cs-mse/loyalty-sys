from postgress.enums import Gender
from datetime import datetime


def validate_date(date_str: str) -> bool:
    if date_str is None:
        return True
    date_format = "%Y-%m"
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


def get_gender(gender):
    try:
        return Gender(gender.lower())
    except:
        print(f"Invalid gender: {gender}")
        return None
