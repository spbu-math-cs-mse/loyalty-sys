import datetime
from psycopg2 import sql

def to_db_readable_date(date):
    return datetime.datetime.strptime(date, "%Y-%m").date()

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