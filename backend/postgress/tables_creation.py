from common import (
    recreate_products_table,
    recreate_purchase_table,
    recreate_enum_gender,
    recreate_enum_discount_type,
    recreate_users_table,
    recreate_purchase_info_table,
    recreate_discounts_table,
    get_connections_pool,
)

if __name__ == "__main__":
    pool = get_connections_pool()
    connection = pool.getconn()

    recreate_enum_gender(connection)
    recreate_enum_discount_type(connection)
    recreate_discounts_table(connection)
    recreate_users_table(connection)
    recreate_products_table(connection)
    recreate_purchase_table(connection)
    recreate_purchase_info_table(connection)

    pool.putconn(connection)
