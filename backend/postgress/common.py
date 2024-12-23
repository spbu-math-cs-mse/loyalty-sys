from postgress.p_utils import (
    to_db_readable_date,
)

import requests

from postgress.enums import DiscountType

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
        update_user_to_discount(connection, user_id)
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

        id, label, price, category_id = cursor.fetchone()

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
            "on (filtered.id = purchase_info.purchase_id)) as joined_purchase"
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

def get_purchase_counts_by_gender(connection):
    try:
        cursor = connection.cursor()
        purchase_counts = [0, 0, 0]

        query = """
        SELECT u.user_gender, COUNT(p.id) AS purchase_count
        FROM users u
        JOIN purchase p ON u.id = p.user_id
        GROUP BY u.user_gender
        """

        cursor.execute(query)
        results = cursor.fetchall()

        for gender, count in results:
            if gender == 'мужской':
                purchase_counts[0] += count
            elif gender == 'женский':
                purchase_counts[1] += count
            else:
                purchase_counts[2] += count
        return purchase_counts

    except Exception as error:
        print(f"Error retrieving purchase counts: {error}")
        return {}

    finally:
        if cursor:
            cursor.close()


def get_median_purchase(connection, start_date, end_date):
    try:
        cursor = connection.cursor()

        joined_purchase = "(SELECT purchase_id, quantity, product_id from purchase_info join (SELECT id from purchase WHERE 1=1"

        if start_date is not None:
            joined_purchase += " AND order_date >= %s"
        if end_date is not None:
            joined_purchase += " AND order_date <= %s"
        joined_purchase += ") as filtered "

        joined_purchase += (
            "on (filtered.id = purchase_info.purchase_id)) as joined_purchase"
        )

        sum_by_purchase = f"""
            (SELECT purchase_id, sum(price_copeck * quantity) as s from 
            {joined_purchase}
            join products on(products.id = product_id)
            GROUP BY purchase_id) as sum_by_purchase
        """

        result = f"SELECT s FROM {sum_by_purchase} ORDER BY s"

        params = []
        if start_date is not None:
            params.append(start_date)
        if end_date is not None:
            params.append(end_date)

        cursor.execute(result, tuple(params))

        sums = cursor.fetchall()
        sums = [row[0] for row in sums]

        n = len(sums)
        if n == 0:
            return 0

        mid_index = n // 2
        sums.sort()

        if n % 2 == 0:
            median = sums[mid_index - 1]
        else:
            median = sums[mid_index]

        return median
    except Exception as error:
        print("Error in get_median_purchase: ", error)
        return None
    finally:
        if cursor:
            cursor.close()

def get_user_birthdays_by_month(connection):
    res = [0] * 12

    try:
        cursor = connection.cursor()
        
        query = """
        SELECT EXTRACT(MONTH FROM birth_date) AS month, COUNT(*) AS count
        FROM users
        GROUP BY month
        ORDER BY month;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()

        for month, count in results:
            if (month == None):
                continue
            res[int(month) - 1] = count

        return res

    except Exception as error:
        print(f"Error in get_user_birthdays_by_month: {error}")
        return [0] * 12

    finally:
        if cursor:
            cursor.close()

def get_products_count_by_category(connection):
    category_count = []

    try:
        cursor = connection.cursor()

        query = """
        SELECT c.id, c.label, COALESCE(SUM(pi.quantity), 0) AS total_quantity
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        LEFT JOIN purchase_info pi ON p.id = pi.product_id
        LEFT JOIN purchase pu ON pi.purchase_id = pu.id
        GROUP BY c.id, c.label;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        category_count_dict = {row[0]: row[2] for row in results}
        
        max_category_id = max(category_count_dict.keys()) if category_count_dict else 0
        category_count = [0] * (max_category_id)

        for category_id, count in category_count_dict.items():
            category_count[category_id - 1] = count
        
        return category_count

    except Exception as error:
        print(f"Error: {error}")
        return [0] * len(get_all_categories(connection))

    finally:
        if cursor:
            cursor.close()

def get_all_categories(connection):
    try:
        categories = []
        cursor = connection.cursor()

        query = """
        SELECT id, label
        FROM categories
        ORDER BY id;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            category = {
                "id": row[0],
                "label": row[1]
            }
            categories.append(category)
            
        return categories

    except Exception as error:
        print(f"Error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()

def insert_admin_record(connection, admin_login, admin_password):
    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO admins (login, password, level) VALUES (%s, %s, %s) RETURNING *;
        """

        cursor.execute(query, (admin_login, admin_password, 0))
        connection.commit()

        return True

    except Exception as error:
        print(f"Error inserting record: {error}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

def check_admin_exists(connection, admin_login, admin_password):
    try:
        cursor = connection.cursor()

        query = """
        SELECT COUNT(*)
        FROM admins
        WHERE login = %s AND password = %s;
        """
        cursor.execute(query, (admin_login, admin_password))
        count = cursor.fetchone()[0]
        exists = count > 0

        return exists

    except Exception as error:
        print(f"Error checking record existence: {error}")

    finally:
        if cursor:
            cursor.close()

def check_admin_exists(connection, admin_login, admin_password):
    try:
        cursor = connection.cursor()

        query = """
        SELECT COUNT(*)
        FROM admins
        WHERE login = %s AND password = %s;
        """
        cursor.execute(query, (admin_login, admin_password))
        count = cursor.fetchone()[0]
        exists = count > 0

        return exists

    except Exception as error:
        print(f"Error checking record existence: {error}")

    finally:
        if cursor:
            cursor.close()



def broadcast_event(connection, name, description, start, end, category, sale):
    try:
        cursor = connection.cursor()
        query = """
        SELECT chat_id FROM users;
        """
 
        cursor.execute(query)
        chats = cursor.fetchall()
        
        url = "http://84.201.143.213:5050/new_event/"
        for chat_id in chats:
            data = {
                "chat_id": chat_id[0],
                "name": name,
                "description": description,
                "start_date": start,
                "end_date": end
            }
            response = requests.post(url, json = data)

        return True

    except Exception as error:
        print(f"Error broadcasting event: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

def loyalty_update(connection, user_id, loyalty_level):
    try:
        cursor = connection.cursor()
        query = """
        SELECT chat_id FROM users WHERE id = %s;
        """
 
        cursor.execute(query, (user_id, ))
        chat_id = cursor.fetchone()
        url = "http://84.201.143.213:5050/loyalty_updates/"
        data = {
            "chat_id": chat_id[0],
            "loyalty_level": loyalty_level
        }
        response = requests.post(url, json = data)

        return True

    except Exception as error:
        print(f"Error in loyalty_update: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

def insert_event_record(connection, name, description, start, end, category, sale):
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO events (name, description, start_date, end_date, category_id, sale) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
        """

        cursor.execute(query, (name, description, to_db_readable_date(start, False), to_db_readable_date(end, False), category, sale))
        connection.commit()

        return True

    except Exception as error:
        print(f"Error inserting event record: {error}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

def update_active(connection, discount_type, status):
    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE discount_type
            SET is_enabled = %s
            WHERE name = %s
        """, (status, discount_type.value))

    except Exception as error:
        print("Error in update_active: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()

def get_active(connection, discount_type):
    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT is_enabled
            FROM discount_type
            WHERE name = %s;
        """, (discount_type.value, ))

        return cursor.fetchone()[0]

    except Exception as error:
        print("Error in get_active: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()

def update_privilages(connection, privilages, discount_type_id):
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, value, money_threshold, type_id FROM discount")
        existing_discounts = {(row[0], "-1")[row[4] != discount_type_id]: row for row in cursor.fetchall()}
        privilages_dict = {p['id']: p for p in privilages}

        for priv_id, priv in privilages_dict.items():
            money_threashold = priv.get('starts_from') * 100
            if priv_id in existing_discounts:
                cursor.execute("""
                    UPDATE discount
                    SET name = %s, value = %s, money_threshold = %s
                    WHERE id = %s AND type_id = %s
                """, (priv.get('label'), priv.get('sale').get('all'), money_threashold, priv_id, discount_type_id))
            else:
                cursor.execute("""
                    INSERT INTO discount (type_id, name, value, money_threshold)
                    VALUES (%s, %s, %s, %s)
                """, (discount_type_id, priv.get('label'), priv.get('sale').get('all'), money_threashold))

        for existing_id in existing_discounts.keys():
            if existing_id not in privilages_dict:
                cursor.execute("""
                    DELETE FROM discount
                    WHERE id = %s AND type_id = %s
                """, (existing_id, discount_type_id, ))

    except Exception as error:
        print("Error in update_privilages: ", error)
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def get_privilages(connection, discount_type_name):
    try:
        cursor = connection.cursor()
        
        query = """
        SELECT d.id, d.name, d.value, d.money_threshold
        FROM discount d
        JOIN discount_type dt ON d.type_id = dt.id
        WHERE dt.name = %s
        """
        
        cursor.execute(query, (discount_type_name,))
        rows = cursor.fetchall()

        print(rows)
        
        privileges = []
        for row in rows:
            privilege = {
                "id": row[0],  
                "label": row[1],  
                "sale": {
                    "all": row[2], 
                },
                "starts_from": row[3] / 100,  
            }
            privileges.append(privilege)
        
        return privileges

    except Exception as error:
        print(f"Error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.commit()


def update_user_to_discount(connection, target_user_id = None):
    try:
        cursor = connection.cursor()
        old_privilaged = {}

        partial_delete = (" WHERE user_id = " + str(target_user_id) + " RETURNING *", "")[target_user_id == None]

        cursor.execute("DELETE FROM user_to_discount" + partial_delete + ";")

        if (target_user_id != None):
            for d_id in [ row[2] for row in cursor.fetchall()]:
                cursor.execute("SELECT type_id, money_threshold FROM discount WHERE id = %s;", (d_id, ))
                result = cursor.fetchone()
                old_privilaged[result[0]] = result[1]
        
        partial_select = (" WHERE id = " + str(target_user_id), "")[target_user_id == None]
        cursor.execute("SELECT id FROM users" + partial_select + ";")
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]

            if (target_user_id != None and target_user_id != user_id):
                continue

            cursor.execute("""
                SELECT SUM(p.price_copeck * pi.quantity) 
                FROM purchase pu
                JOIN purchase_info pi ON pu.id = pi.purchase_id
                JOIN products p ON pi.product_id = p.id
                WHERE pu.user_id = %s;
            """, (user_id,))
            total_sum = cursor.fetchone()[0] or 0

            query = """
                SELECT d.id, d.type_id, d.money_threshold, d.name, d.value, dt.name, dt.is_enabled
                FROM discount d
                JOIN discount_type dt ON d.type_id = dt.id
                WHERE d.money_threshold <= %s AND dt.name = %s
                ORDER BY d.money_threshold DESC
                LIMIT 1;
            """

            cursor.execute(query, (total_sum, DiscountType.SALE.value, ))
            discount = cursor.fetchone()

            if discount:
                discount_id = discount[0]
                cursor.execute("""
                    INSERT INTO user_to_discount (user_id, discount_id) 
                    VALUES (%s, %s);
                """, (user_id, discount_id))

                if (target_user_id != None):
                    if (discount[2] > old_privilaged.get(discount[1], 1000000) and discount[6]):
                        loyalty_update(connection, target_user_id, (discount[3], discount[4], discount[5]))
                    

            
            cursor.execute(query, (total_sum, DiscountType.POINTS.value, ))

            discount = cursor.fetchone()
            if discount:
                discount_id = discount[0]
                cursor.execute("""
                    INSERT INTO user_to_discount (user_id, discount_id) 
                    VALUES (%s, %s);
                """, (user_id, discount_id))

                if (target_user_id != None):
                    if (discount[2] > old_privilaged.get(discount[1], 1000000) and discount[6]):
                        loyalty_update(connection, target_user_id, (discount[3], discount[4], discount[5]))

    except Exception as error:
        print(f"An error occurred in update_user_to_discount: {error}")
        return None

    finally:
        if cursor:
            cursor.close()
        connection.commit()


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

        test_q = """
            SELECT * FROM users
        """

        cursor.execute(base_query, [user_id])

        result = [(type_name, name, value, threshold) for type_name, name, value, threshold in cursor.fetchall()]
        
        cursor.execute(test_q)
        print(cursor.fetchall())

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
