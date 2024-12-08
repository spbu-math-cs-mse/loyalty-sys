import os
import psycopg2
from dotenv import load_dotenv


MAX_POOL_CONNECTIONS = 50

def c():
    load_dotenv()
    return psycopg2.pool.SimpleConnectionPool(
        1,
        MAX_POOL_CONNECTIONS,
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOSTS"),
        port=os.getenv("DB_PORT"),
    )