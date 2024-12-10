from postgress.utils import (
    to_db_readable_date,
)
from psycopg2 import sql

def find_or_create_user(connection, chat_id):
    try:
        created = False
        cursor = connection.cursor()

        find_user_query = sql.SQL("SELECT * FROM users WHERE chat_id = %s;")
        cursor.execute(find_user_query, (chat_id,))
        
        user = cursor.fetchone()

        if user:
            user_id, chat_id, gender, birth_date = user
            return user_id, created

        insert_user_query = sql.SQL(
            "INSERT INTO users (chat_id) VALUES (%s) RETURNING *;"
        )
        cursor.execute(insert_user_query, (chat_id,))

        created = True
        user_id, chat_id, gender, birth_date = cursor.fetchone()
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

def get_purchases_sum(connection, start_date, end_date, user_id=None):
    try:
        cursor = connection.cursor()

        joined_purchase = "(SELECT purchase_id, quantity, product_id from purchase_info join (SELECT id from purchase WHERE 1=1"

        if start_date is not None:
            joined_purchase += " AND order_date >= %s"
        if end_date is not None:
            joined_purchase += " AND order_date <= %s"
        if user_id is not None:
            joined_purchase += " AND user_id = %s"
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

        result = f"SELECT COALESCE(sum(s), 0) from {sum_by_purchase}"

        params = []
        if start_date is not None:
            params.append(to_db_readable_date(start_date))
        if end_date is not None:
            params.append(to_db_readable_date(end_date))
        if user_id is not None:
            params.append(user_id)

        cursor.execute(result, tuple(params))

        # fetchone returns row with 1 element
        purchases_count = cursor.fetchone()[0]
        return purchases_count
    except Exception as error:
        print("Error in get_purchases_sum: ", error)
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


def get_visitors_count(connection):
    try:
        cursor = connection.cursor()

        base_query = "SELECT COALESCE(SUM(1), 0) FROM users WHERE 1=1"

        cursor.execute(base_query)

        # fetchone returns row with 1 element
        users_count = cursor.fetchone()[0]
        return users_count
    except Exception as error:
        print("Error in get_visitors_count: ", error)
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


def get_loyalty_level(connection, user_id):
    try:
        cursor = connection.cursor()

        base_query = """
            SELECT 
                dt.name AS discount_type_name,
                d.name AS discount_name,
                d.value AS discount_value,
                d.money_threshold AS discount_threshold
            FROM 
                users u
            JOIN 
                user_to_discount ud ON u.id = ud.user_id
            JOIN 
                discount d ON ud.discount_id = d.id
            JOIN 
                discount_type dt ON d.type_id = dt.id
            WHERE 
                u.id = %s AND 
                dt.is_enabled = TRUE;
        """

        cursor.execute(base_query, [user_id])

        result = [(type_name, name, value, threshold) for type_name, name, value, threshold in cursor.fetchall()]

        return result
    except Exception as error:
        print("Error in get_loyalty_level: ", error)
        return None

    finally:
        if cursor:
            cursor.close()


def update_user_discount(connection, user_id, new_discount_id, old_discount_id):
    try:
        cursor = connection.cursor()

        base_query = "UPDATE user_to_discount SET discount_id = %s WHERE user_id = %s AND discount_id = %s"

        cursor.execute(base_query, (new_discount_id, user_id, old_discount_id))

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

def set_birthday(connection, user_id, user_birthday):
    try:
        cursor = connection.cursor()

        base_query = "UPDATE users SET birth_date = %s WHERE id = %s"
        print(user_birthday)

        cursor.execute(base_query, (to_db_readable_date(user_birthday, False), user_id))

        return True
    except Exception as error:
        print("Error in set_birthday: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def add_admin(connection, login, password, level):
    try:
        created = False
        cursor = connection.cursor()
        
        insert_admin_query = sql.SQL(
            "INSERT INTO admins (login, password, level) VALUES (%s, %s, %s) RETURNING *;"
        )
        cursor.execute(insert_admin_query, (login, password, level))

        created = True
        return user_id, created
    except Exception as error:
        print("Error in find_or_create_user: ", error)
        connection.rollback()
        return None, False

    finally:
        if cursor:
            cursor.close()
        connection.commit()
