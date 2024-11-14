from enum import Enum


class Message(Enum):
    USER_CREATED = "User created"
    USER_ALREADY_EXISTS = "User already exists"
    PURCHASES_RECORDED = "Purchases recorded"
    INVALID_DATE_FORMAT = "Invalid date format. Use %Y-%m."
    NO_PURCHASES_PROVIDED = "No purchases provided"
    INVALID_PURCHASE_DATA = "Invalid purchase data"
    CHAT_ID_REQUIRED = "Chat id is required"
    CHAT_ID_TYPE = "Chat id must be sting"
    PRODUCT_ID_REQUIRED = "Product id is required"
    DB_ERROR = "DB error"
