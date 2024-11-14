import os
import datetime

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
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {table_schema}
            );
        """
        )

        cursor.execute(create_table_query)

        connection.commit()
    except Exception as error:
        print(f"Error occurred in recreate_table {table_name}: {error}")
    finally:
        if cursor:
            cursor.close()


def recreate_users_table(connection, should_drop=True):
    recreate_table(
        connection,
        "users",
        """id SERIAL PRIMARY KEY,
        chat_id VARCHAR(255) NOT NULL
        """,
        should_drop,
    )


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


def find_or_create_user(connection, chat_id):
    try:
        created = False
        cursor = connection.cursor()

        find_user_query = sql.SQL("SELECT * FROM users WHERE chat_id = %s;")
        cursor.execute(find_user_query, (chat_id,))

        user = cursor.fetchone()

        if user:
            return user[0], created

        insert_user_query = sql.SQL(
            "INSERT INTO users (chat_id) VALUES (%s) RETURNING *;"
        )
        cursor.execute(insert_user_query, (chat_id,))

        created = True
        return cursor.fetchone()[0], created

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

        return cursor.fetchone()[0]
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
        raise

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def get_product_statistic(connection, product_id, start_date, end_date):
    try:
        cursor = connection.cursor()
        base_query = """
            SELECT
                DATE_TRUNC('month', order_date) AS month,
                SUM(quantity) AS total_quantity
            FROM
                (SELECT order_date, quantity, product_id FROM purchase JOIN purchase_info on (purchase.id = purchase_info.purchase_id)) tmp
            WHERE
                product_id = %s
            """

        if start_date is not None:
            base_query += " AND order_date >= %s"
        if end_date is not None:
            base_query += " AND order_date <= %s"

        base_query += """
            GROUP BY
                month
            ORDER BY
                month;
            """

        params = [product_id]
        if start_date is not None:
            params.append(to_db_readable_date(start_date))
        if end_date is not None:
            params.append(to_db_readable_date(end_date))

        cursor.execute(base_query, tuple(params))
        results = cursor.fetchall()

        find_product_query = sql.SQL("SELECT * FROM products WHERE id = %s;")

        cursor.execute(find_product_query, (product_id,))

        product_label = cursor.fetchone()[1]
        return results, product_label

    except Exception as error:
        print("Error in get_product_statistic: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_purchases_count(connection, start_date, end_date):
    try:
        cursor = connection.cursor()

        base_query = """
            SELECT
                SUM(1)
            FROM
                purchase_info JOIN purchase on (purchase.id = purchase_id)
            WHERE 1=1
            """

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

        return cursor.fetchone()
    except Exception as error:
        print("Error in get_purchases_count: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_average_purchase(connection, start_date, end_date):
    try:
        cursor = connection.cursor()

        joined_purchase = """
            (SELECT purchase_id, quantity, product_id from
            purchase_info join 
            (SELECT id from purchase WHERE 1=1
        """
        if start_date is not None:
            joined_purchase += " AND order_date >= %s"
        if end_date is not None:
            joined_purchase += " AND order_date <= %s"
        joined_purchase += ") as filtered "

        joined_purchase += """on (filtered.id = purchase_info.product_id)) as joined_purchase
        """

        sum_by_purchase = f"""
            (SELECT purchase_id, sum(price_copeck * quantity) as s from 
            {joined_purchase}
            join products on(products.id = product_id)
            GROUP BY purchase_id) as sum_by_purchase
        """

        result = f"""SELECT avg(s) from {sum_by_purchase}"""

        params = []
        if start_date is not None:
            params.append(start_date)
        if end_date is not None:
            params.append(end_date)

        cursor.execute(result, tuple(params))

        return cursor.fetchone()
    except Exception as error:
        print("Error in get_average_purchase: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_visits_count(connection, start_date, end_date):
    try:
        cursor = connection.cursor()

        base_query = """
            SELECT
                SUM(1)
            FROM
                purchase
            WHERE 1=1
            """

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

        return cursor.fetchone()
    except Exception as error:
        print("Error in get_visitors_count: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def get_all_products(connection):
    try:
        cursor = connection.cursor()

        base_query = """
            SELECT
                *
            FROM
                products
            """

        cursor.execute(base_query)

        return cursor.fetchall()
    except Exception as error:
        print("Error in get_all_products: ", error)
        return None

    finally:
        if cursor:
            cursor.close()
