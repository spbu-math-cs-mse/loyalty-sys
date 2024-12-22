from enums import (Gender, DiscountType)
from psycopg2 import sql

from utils import (
    recreate_enum,
    recreate_table,
)

from connection_setup import get_connections_pool

# ================= GENDER ==================

def recreate_enum_gender(connection, should_drop=True):
    recreate_enum(
        connection,
        "gender",
        f"{','.join([f"'{gender.value}'" for gender in Gender])}",
        should_drop,
    )


# ================= DISCOUNT ==================

def fill_discount_type_table(connection):
    try:
        cursor = connection.cursor()
        insert_user_query = sql.SQL(
            "INSERT INTO discount_type (name, is_enabled) VALUES (%s, %s);"
        )

        for discount_type in DiscountType:
            cursor.execute(insert_user_query, (discount_type.value, False))
    except Exception as error:
        print(f"Error occurred in fill_discount_type_table: {error}")
    finally:
        if cursor:
            cursor.close()
        connection.commit()
        
# TODO: think about some config file with types 
def recreate_discount_type_table(connection, should_drop=True, fill_table=True):
    recreate_table(
        connection,
        "discount_type",
        """id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            is_enabled BOOLEAN NOT NULL
        """,
        should_drop,
    )
    if fill_table:
        fill_discount_type_table(connection)


def recreate_discount_table(connection, should_drop=True):
    recreate_table(
        connection,
        "discount",
        """id SERIAL PRIMARY KEY,
            type_id INTEGER NOT NULL,
            name VARCHAR(255) NULL,
            value SMALLINT NULL,
            money_threshold BIGINT NULL,
            FOREIGN KEY (type_id) REFERENCES discount_type (id)
        """,
        should_drop,
    )


def recreate_user_to_discount_table(connection, should_drop=True):
    recreate_table(
        connection,
        "user_to_discount",
        """ id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            discount_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (discount_id) REFERENCES discount (id)
        """,
        should_drop,
    )

# ================= USER ===================

def recreate_users_table(connection, should_drop=True):
    recreate_table(
        connection,
        "users",
        """id SERIAL PRIMARY KEY,
        chat_id VARCHAR(255) NOT NULL,
        user_gender gender NULL,
        birth_date DATE NULL
        """,
        should_drop,
    )

# ================= ADMIN ===================


def fill_admin(connection):
    try:
        cursor = connection.cursor()
        insert_admin_query = sql.SQL(
            "INSERT INTO admins (login, password, level) VALUES (%s, %s, %s) RETURNING *;"
        )

        cursor.execute(insert_admin_query, ("admin", "c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec", 0))
    except Exception as error:
        print(f"Error occurred in fill_admin: {error}")
    finally:
        if cursor:
            cursor.close()
        connection.commit()
        

def recreate_admins_table(connection, should_drop=True):
    recreate_table(
        connection,
        "admins",
        """id SERIAL PRIMARY KEY,
        login VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        level SMALLINT NOT NULL
        """,
        should_drop,
    )

    if (should_drop):
        fill_admin(connection)


# ================= PRODUCT ===================

# TODO(vvsg): change this function with handle/loading from file
def fill_products_table(connection):
    try:
        cursor = connection.cursor()
        # HIGHLY DANGEROUS WAY TO SET CATEGORY
        # TODO: rewrite as soon as possible
        insert_user_query = sql.SQL(
            "INSERT INTO products (label, price_copeck, category_id) VALUES (%s, %s, %s);"
        )

        cursor.execute(insert_user_query, ("Apple", 1000, 1))
        cursor.execute(insert_user_query, ("Orange", 2003, 1))
        cursor.execute(insert_user_query, ("Chocolate", 100000, 1))
        cursor.execute(insert_user_query, ("Iphone", 20_000_000, 2))
        cursor.execute(insert_user_query, ("Chair", 400_000, 3))
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
        price_copeck BIGINT CHECK (price_copeck >= 1),
        category_id INTEGER NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
        """,
        should_drop,
    )

    if fill_table:
        fill_products_table(connection)

# TODO(vvsg): change this function with handle/loading from file and unite with fill_products_table
def fill_categories_table(connection):
    try:
        cursor = connection.cursor()
        insert_query = sql.SQL(
            "INSERT INTO categories (label) VALUES (%s);"
        )

        cursor.execute(insert_query, ["Food"])
        cursor.execute(insert_query, ["Device"])
        cursor.execute(insert_query, ["Furniture"])
    except Exception as error:
        print(f"Error occurred in fill_categories_table: {error}")
    finally:
        if cursor:
            cursor.close()
        connection.commit()

def recreate_categories_table(connection, should_drop=True, fill_table=True):
    recreate_table(
        connection,
        "categories",
        """id SERIAL PRIMARY KEY,
        label VARCHAR(255) NOT NULL
        """,
        should_drop,
    )

    if fill_table:
        fill_categories_table(connection)

# ================= PURCHASE ===================

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

# ================= POINT ===================

def recreate_points_table(connection, should_drop=True):
    recreate_table(
        connection,
        "points",
        """id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            number BIGINT CHECK (number >= 1),
            lifetime DATE NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        """,
        should_drop,
    )

# ================= EVENT ===================

def recreate_events_table(connection, should_drop=True):
    recreate_table(
        connection,
        "events",
        """id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            start_date DATE NULL,
            end_date DATE NOT NULL,
            category_id INTEGER NULL,
            sale SMALLINT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        """,
        should_drop,
    )

if __name__ == "__main__":
    pool = get_connections_pool()
    connection = pool.getconn()

    recreate_enum_gender(connection)

    recreate_discount_type_table(connection)
    recreate_discount_table(connection)
    recreate_user_to_discount_table(connection)

    recreate_categories_table(connection)
    recreate_products_table(connection)

    recreate_purchase_table(connection)
    recreate_purchase_info_table(connection)

    recreate_users_table(connection)

    recreate_points_table(connection)

    recreate_admins_table(connection)
    recreate_events_table(connection)

    pool.putconn(connection)
