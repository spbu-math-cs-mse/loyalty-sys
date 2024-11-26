import os
import datetime

from enum import Enum

import psycopg2
from psycopg2 import sql, pool
from dotenv import load_dotenv


MAX_POOL_CONNECTIONS = 50


def to_db_readable_date(date):
    return datetime.datetime.strptime(date, "%Y-%m").date()


def get_connections_pool():
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


def recreate_table(connection, table_name, table_schema, should_drop=True):
    try:
        cursor = connection.cursor()

        if should_drop:
            drop_table_query = sql.SQL(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            cursor.execute(drop_table_query)

        create_table_query = sql.SQL(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({table_schema});"
        )

        cursor.execute(create_table_query)

        connection.commit()
    except Exception as error:
        print(f"Error occurred in recreate_table {table_name}: {error}")
    finally:
        if cursor:
            cursor.close()


def recreate_enum(connection, enum_name, enum_values, should_drop):
    try:
        cursor = connection.cursor()

        if should_drop:
            drop_type_query = sql.SQL(f"DROP TYPE IF EXISTS {enum_name} CASCADE")
            cursor.execute(drop_type_query)

        create_type_query = sql.SQL(f"CREATE TYPE {enum_name} AS ENUM ({enum_values})")

        cursor.execute(create_type_query)

        connection.commit()
    except Exception as error:
        print(f"Error occurred in recreate_type_gender {enum_name}: {error}")
    finally:
        if cursor:
            cursor.close()


class Gender(Enum):
    MAN = "man"
    WOMAN = "woman"


def recreate_enum_gender(connection, should_drop=True):
    recreate_enum(
        connection,
        "gender",
        f"{','.join([f"'{gender.value}'" for gender in Gender])}",
        should_drop,
    )


class DiscountType(Enum):
    POINTS = "points"
    SALE = "sale"


def recreate_enum_discount_type(connection, should_drop=True):
    recreate_enum(
        connection,
        "discount_type",
        f"{','.join([f"'{type.value}'" for type in DiscountType])}",
        should_drop,
    )


def recreate_users_table(connection, should_drop=True):
    recreate_table(
        connection,
        "users",
        """id SERIAL PRIMARY KEY,
        chat_id VARCHAR(255) NOT NULL,
        user_gender gender NULL,
        discount_id INTEGER NULL,
        FOREIGN KEY (discount_id) REFERENCES discounts (id)
        """,
        should_drop,
    )


# TODO(vvsg): change this function with handle/loading from file
def fill_products_table(connection):
    try:
        cursor = connection.cursor()
        insert_user_query = sql.SQL(
            "INSERT INTO products (label, price_copeck) VALUES (%s, %s);"
        )

        cursor.execute(insert_user_query, ("Apple", 1000))
        cursor.execute(insert_user_query, ("Orange", 2003))
        cursor.execute(insert_user_query, ("Chocolate", 100000))
        cursor.execute(insert_user_query, ("Iphone", 20_000_000))
        cursor.execute(insert_user_query, ("Chair", 400_000))
    except Exception as error:
        print(f"Error occurred in fill_products_table: {error}")
    finally:
        if cursor:
            cursor.close()
        connection.commit()


def recreate_products_table(connection, should_drop=True, fill_table=True):
    recreate_table(
        connection,
        "products",
        """id SERIAL PRIMARY KEY,
        label VARCHAR(255) NOT NULL,
        price_copeck INTEGER CHECK (price_copeck >= 1)
        """,
        should_drop,
    )

    if fill_table:
        fill_products_table(connection)


def recreate_purchase_table(connection, should_drop=True):
    recreate_table(
        connection,
        "purchase",
        """ id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        """,
        should_drop,
    )


def recreate_purchase_info_table(connection, should_drop=True):
    recreate_table(
        connection,
        "purchase_info",
        """ id SERIAL PRIMARY KEY,
            purchase_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity DOUBLE PRECISION NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (purchase_id) REFERENCES purchase (id)
        """,
        should_drop,
    )


def recreate_discounts_table(connection, should_drop=True, fill_table=True):
    recreate_table(
        connection,
        "discounts",
        """ id SERIAL PRIMARY KEY,
            type discount_type NOT NULL,
            level INTEGER NOT NULL
        """,
        should_drop,
    )

    if fill_table:
        fill_discounts_table(connection)


# TODO(vvsg): change this function with handle/loading from file
def fill_discounts_table(connection):
    try:
        cursor = connection.cursor()
        insert_query = sql.SQL("INSERT INTO discounts (type, level) VALUES (%s, %s);")

        cursor.execute(insert_query, ("points", 2))
        cursor.execute(insert_query, ("points", 0))
        cursor.execute(insert_query, ("points", 10))
        cursor.execute(insert_query, ("sale", 11))
        cursor.execute(insert_query, ("sale", 23))
    except Exception as error:
        print(f"Error occurred in fill_discounts_table: {error}")
    finally:
        if cursor:
            cursor.close()
        connection.commit()


def find_or_create_user(connection, chat_id):
    try:
        created = False
        cursor = connection.cursor()

        find_user_query = sql.SQL("SELECT * FROM users WHERE chat_id = %s;")
        cursor.execute(find_user_query, (chat_id,))

        user = cursor.fetchone()

        if user:
            user_id, chat_id, gender, discount = user
            return user_id, created

        insert_user_query = sql.SQL(
            "INSERT INTO users (chat_id) VALUES (%s) RETURNING *;"
        )
        cursor.execute(insert_user_query, (chat_id,))

        created = True
        user_id, chat_id, gender, discount = cursor.fetchone()
        return user_id, created
    except Exception as error:
        print("Error in find_or_create_user: ", error)
        connection.rollback()
        return None, False

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def insert_purchase(connection, user_id, date):
    try:
        cursor = connection.cursor()

        insert_purchase_query = sql.SQL(
            "INSERT INTO purchase (user_id, order_date) VALUES (%s, %s) RETURNING *;"
        )
        cursor.execute(insert_purchase_query, (user_id, to_db_readable_date(date)))

        id, user_id, order_date = cursor.fetchone()
        return id
    except Exception as error:
        print("Error in insert_purchase: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def insert_purchase_info(connection, purchase_id, product_id, quantity):
    try:
        cursor = connection.cursor()

        insert_purchase_query = sql.SQL(
            "INSERT INTO purchase_info (purchase_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING *;"
        )
        cursor.execute(insert_purchase_query, (purchase_id, product_id, quantity))

        return cursor.fetchone()
    except Exception as error:
        print("Error in insert_purchase_info: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def get_product_statistic(connection, product_id, start_date, end_date):
    try:
        cursor = connection.cursor()
        base_query = """
            WITH date_series AS (
                SELECT generate_series(
                    %s::date,
                    %s::date,
                    '1 month'
                )::date AS month_start
            ),
            
            purchase_full AS (
                SELECT order_date, quantity, product_id FROM purchase JOIN 
                    purchase_info on (purchase.id = purchase_info.purchase_id)
                WHERE
                    product_id = %s AND order_date >= %s AND order_date <= %s
            )

            SELECT
                to_char(date_series.month_start, 'YYYY-MM') AS month,
                COALESCE(SUM(purchase_full.quantity), 0) AS total_quantity
            FROM
                date_series LEFT JOIN purchase_full on to_char(purchase_full.order_date, 'YYYY-MM') = to_char(date_series.month_start, 'YYYY-MM') 
            GROUP BY
                month
            ORDER BY
                month;
            """

        start = to_db_readable_date(start_date)
        end = to_db_readable_date(end_date)
        cursor.execute(
            base_query,
            (start, end, product_id, start, end),
        )

        qualities = [total_quality for month, total_quality in cursor.fetchall()]

        find_product_query = sql.SQL("SELECT * FROM products WHERE id = %s;")

        cursor.execute(find_product_query, (product_id,))

        id, label, price = cursor.fetchone()

        return qualities, label
    except Exception as error:
        print("Error in get_product_statistic: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_purchases_count(connection, start_date, end_date, user_id=None):
    try:
        cursor = connection.cursor()

        base_query = "SELECT COALESCE(SUM(1), 0) FROM purchase_info JOIN purchase on (purchase.id = purchase_id) WHERE 1=1"

        if start_date is not None:
            base_query += " AND order_date >= %s"
        if end_date is not None:
            base_query += " AND order_date <= %s"
        if user_id is not None:
            base_query += " AND user_id = %s"

        params = []
        if start_date is not None:
            params.append(to_db_readable_date(start_date))
        if end_date is not None:
            params.append(to_db_readable_date(end_date))
        if user_id is not None:
            params.append(user_id)

        cursor.execute(base_query, tuple(params))

        # fetchone returns row with 1 element
        purchases_count = cursor.fetchone()[0]
        return purchases_count
    except Exception as error:
        print("Error in get_purchases_count: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_average_purchase(connection, start_date, end_date):
    try:
        cursor = connection.cursor()

        joined_purchase = "(SELECT purchase_id, quantity, product_id from purchase_info join (SELECT id from purchase WHERE 1=1"

        if start_date is not None:
            joined_purchase += " AND order_date >= %s"
        if end_date is not None:
            joined_purchase += " AND order_date <= %s"
        joined_purchase += ") as filtered "

        joined_purchase += (
            "on (filtered.id = purchase_info.product_id)) as joined_purchase"
        )

        sum_by_purchase = f"""
            (SELECT purchase_id, sum(price_copeck * quantity) as s from 
            {joined_purchase}
            join products on(products.id = product_id)
            GROUP BY purchase_id) as sum_by_purchase
        """

        result = f"SELECT COALESCE(avg(s), 0) from {sum_by_purchase}"

        params = []
        if start_date is not None:
            params.append(start_date)
        if end_date is not None:
            params.append(end_date)

        cursor.execute(result, tuple(params))

        # fetchone returns row with 1 element
        average_check = cursor.fetchone()[0]

        return average_check
    except Exception as error:
        print("Error in get_average_purchase: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_visits_count(connection, start_date, end_date):
    try:
        cursor = connection.cursor()

        base_query = "SELECT COALESCE(SUM(1), 0) FROM purchase WHERE 1=1"

        if start_date is not None:
            base_query += " AND order_date >= %s"
        if end_date is not None:
            base_query += " AND order_date <= %s"

        params = []
        if start_date is not None:
            params.append(to_db_readable_date(start_date))
        if end_date is not None:
            params.append(to_db_readable_date(end_date))

        cursor.execute(base_query, tuple(params))

        # fetchone returns row with 1 element
        users_count = cursor.fetchone()[0]
        return users_count
    except Exception as error:
        print("Error in get_visitors_count: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_all_products(connection):
    try:
        cursor = connection.cursor()

        base_query = "SELECT * FROM products"

        cursor.execute(base_query)

        return cursor.fetchall()
    except Exception as error:
        print("Error in get_all_products: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_user_discount(connection, user_id):
    try:
        cursor = connection.cursor()

        base_query = "SELECT discount_type, level FROM users JOIN discounts on (discounts.id = users.discount_id) where users.id = %s"

        cursor.execute(base_query, (user_id))

        return cursor.fetchall()
    except Exception as error:
        print("Error in get_user_discount: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def set_user_discount(connection, user_id, discount_id):
    try:
        cursor = connection.cursor()

        base_query = "UPDATE users SET discount_id = %s WHERE id = %s"

        cursor.execute(base_query, (discount_id, user_id))

        return True
    except Exception as error:
        print("Error in set_user_discount: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def set_gender(connection, user_id, user_gender):
    try:
        cursor = connection.cursor()

        base_query = "UPDATE users SET user_gender = %s WHERE id = %s"

        cursor.execute(base_query, (user_gender.value, user_id))

        return True
    except Exception as error:
        print("Error in set_gender: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()
