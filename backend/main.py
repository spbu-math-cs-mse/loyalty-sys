import argparse

from flask import Flask, request, jsonify
from flask_cors import CORS
from message import Message

from utils import validate_date, get_gender

from postgress.connection_setup import get_connections_pool

from postgress.enums import(
    DiscountType
)

from postgress.common import (
    find_or_create_user,
    insert_purchase,
    insert_purchase_info,
    get_product_statistic,
    get_purchases_count,
    get_loyalty_level,
    get_purchases_sum,
    get_average_purchase,
    get_median_purchase,
    get_user_birthdays_by_month,
    get_all_categories,
    get_products_count_by_category,
    get_purchase_counts_by_gender,
    insert_admin_record,
    insert_event_record,
    check_admin_exists,
    get_visits_count,
    get_visitors_count,
    get_all_products,
    set_gender,
    set_birthday,
    update_user_discount,
    update_active,
    update_privilages,
    update_user_to_discount,
    get_active,
    get_privilages,
    broadcast_event,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app)

connection_pool = None


with app.app_context():
    connection_pool = get_connections_pool()

@app.route("/privileges", methods=["GET"])
def get_privileges():
    try:
        connection = connection_pool.getconn()
        print(get_active(connection,  DiscountType.SALE))
        print(get_active(connection,  DiscountType.POINTS))
        print(get_privilages(connection, DiscountType.SALE.value))
        print(get_privilages(connection, DiscountType.POINTS.value))
        return jsonify({
                "percent": {
                  "settings": {
                    "active": get_active(connection,  DiscountType.SALE),
                    "levels": 5,
                  },
                  "privileges": get_privilages(connection, DiscountType.SALE.value),
                },
                "point": {
                  "settings": {
                    "active": get_active(connection,  DiscountType.POINTS),
                    "levels": 15,
                  },
                  "privileges": get_privilages(connection, DiscountType.POINTS.value),
                },
            })
    finally:
        connection_pool.putconn(connection)
    return jsonify({"message": "Feedback"}), 200
    return jsonify(privileges), 200


@app.route("/privileges", methods=["POST"])
def send_privileges():
    data = request.json.get("settings")
    print(data)
    percent_active = data.get("percent").get("settings").get("active")
    percent_privilages = [ elem for elem in data.get("percent").get("privileges")] 
    point_active = data.get("point").get("settings").get("active")
    point_privilages = [ elem for elem in data.get("point").get("privileges")]
    try:
        connection = connection_pool.getconn()
        update_active(connection, DiscountType.SALE, percent_active)
        update_active(connection, DiscountType.POINTS, point_active)

        update_privilages(connection, percent_privilages, 1)
        update_privilages(connection, point_privilages, 2)

        update_user_to_discount(connection)
        return jsonify({})
    finally:
        connection_pool.putconn(connection)
    return jsonify({"message": "Feedback"}), 200

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    chat_id = data.get("chat_id")

    if not chat_id:
        return jsonify({"message": Message.CHAT_ID_REQUIRED.value}), 400

    if not isinstance(chat_id, str):
        return jsonify({"message": Message.CHAT_ID_TYPE.value}), 400
    try:
        connection = connection_pool.getconn()

        user_id, created = find_or_create_user(connection, chat_id)

        if not user_id:
            return jsonify({"message": Message.DB_ERROR.value}), 502

        if created:
            return (
                jsonify({"message": Message.USER_CREATED.value, "user_id": user_id}),
                201,
            )
        else:
            return (
                jsonify(
                    {"message": Message.USER_ALREADY_EXISTS.value, "user_id": user_id}
                ),
                200,
            )
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/purchase", methods=["POST"])
def record_purchase(user_id: int):
    data = request.json
    purchases_list = data.get("purchases", [])
    date = data.get("date")

    if not purchases_list:
        return jsonify({"message": Message.NO_PURCHASES_PROVIDED.value}), 400

    if not isinstance(purchases_list, list):
        return jsonify({"message": Message.WRONG_PURCHASES_TYPE.value}), 400

    if not date or not validate_date(date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()

        purchase_id = insert_purchase(connection, user_id, date)
        for item in purchases_list:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if product_id is None or quantity is None:
                return jsonify({"message": Message.INVALID_PURCHASE_DATA.value}), 400

            insert_purchase_info(connection, purchase_id, product_id, quantity)

        update_user_to_discount(connection, user_id)

        return (
            jsonify(
                {
                    "message": Message.PURCHASES_RECORDED.value,
                    "purchase_id": purchase_id,
                },
            ),
            201,
        )
    except Exception as error:
        return (jsonify({"message": Message.DB_ERROR.value, "error": str(error)}), 400)
    finally:
        connection_pool.putconn(connection)


@app.route("/data/values", methods=["GET"])
def get_product_values():
    product_id = request.args.get("product_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if product_id is None:
        return jsonify({"message": Message.PRODUCT_ID_REQUIRED.value}), 400

    if (
        not start_date
        or not validate_date(start_date)
        or not end_date
        or not validate_date(end_date)
    ):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        statistics, product_label = get_product_statistic(
            connection, product_id, start_date, end_date
        )
        return jsonify(
            {"label": product_label, "values": [element for element in statistics]}
        )
    finally:
        connection_pool.putconn(connection)


@app.route("/data/total_purchases", methods=["GET"])
def get_total_purchases():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_purchases_sum(connection, start_date, end_date)
        return jsonify({"total_purchases": result})
    finally:
        connection_pool.putconn(connection)


@app.route("/data/average_check", methods=["GET"])
def get_average_check():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_average_purchase(connection, start_date, end_date)
        return jsonify({"average_check": result})
    finally:
        connection_pool.putconn(connection)

@app.route("/data/median_check", methods=["GET"])
def get_median_check():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_median_purchase(connection, start_date, end_date)
        return jsonify({"median_check": result})
    finally:
        connection_pool.putconn(connection)

@app.route("/data/buys_bithdays", methods=["GET"])
def get_buys_bithdays():
    try:
        connection = connection_pool.getconn()
        result = get_user_birthdays_by_month(connection)
        print(result)
        return result
    finally:
        connection_pool.putconn(connection)

@app.route("/data/buys_category", methods=["GET"])
def get_buys_category():
    try:
        print("get_buys_category")
        connection = connection_pool.getconn()
        result = get_products_count_by_category(connection)
        print(result)
        return jsonify(result)
    finally:
        connection_pool.putconn(connection)

@app.route("/data/buys_more", methods=["GET"])
def get_buys_more():
    try:
        print("buys_more")
        connection = connection_pool.getconn()
        result = get_purchase_counts_by_gender(connection)
        return jsonify(result)
    finally:
        connection_pool.putconn(connection)

@app.route("/data/categories", methods=["GET"])
def get_categories():
    try:
        connection = connection_pool.getconn()
        result = get_all_categories(connection)
        print(result)
        return result
    finally:
        connection_pool.putconn(connection)


@app.route("/data/visitor_count", methods=["GET"])
def get_visitor_count():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_visitors_count(connection)
        return jsonify({"visitor_count": result})
    finally:
        connection_pool.putconn(connection)


@app.route("/data/products", methods=["GET"])
def get_products():
    try:
        connection = connection_pool.getconn()
        result = get_all_products(connection)
        return jsonify(
            [
                {"id": id, "label": label, "price_copeck": price}
                for id, label, price, category in result
            ]
        )
    finally:
        connection_pool.putconn(connection)


# @app.route("/user/<int:user_id>/discount", methods=["GET"])
# def get_user_discount_api(user_id: int):
#     try:
#         connection = connection_pool.getconn()
#         # TODO: update
#         result = get_loyalty_level(connection, user_id)

#         if result is None:
#             return (
#                 jsonify({"type": "no discount yet", "value": None}),
#                 200,
#             )

#         discount_type, level = "Скидка", "Не определён" if len(result) == 0 else result[0]

#         return (
#             jsonify({"type": discount_type, "value": level}),
#             200,
#         )
#     finally:
#         connection_pool.putconn(connection)


# @app.route("/user/<int:user_id>/discount", methods=["PUT"])
# def set_user_discount_api(user_id: int):
#     try:
#         connection = connection_pool.getconn()
#         discount_id = request.json.get("discount_id")
#         if not discount_id:
#             return jsonify({"message": Message.NO_DISCOUNT.value}), 400

#         # TODO: change to update_user_discount here
#         result = set_user_discount(connection, user_id, discount_id)

#         if result is None:
#             return jsonify({"message": Message.INVALID_DISCOUNT.value}), 400

#         return jsonify({"message": Message.DISCOUNT_UPDATED.value}), 200
#     finally:
#         connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/total_purchases", methods=["GET"])
def get_user_total_purchases_api(user_id: int):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_purchases_sum(connection, start_date, end_date, user_id) / 100
        return jsonify({"total_purchases": result})
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/loyalty_level", methods=["GET"])
def get_user_loyalty_level_api(user_id: int):

    try:
        connection = connection_pool.getconn()
        loyalty_level = get_loyalty_level(connection, user_id)
        return jsonify({"loyalty_level": loyalty_level})
    finally:
        connection_pool.putconn(connection)



@app.route("/user/<int:user_id>/gender", methods=["PUT"])
def update_user_gender_api(user_id: int):
    data = request.json
    gender = data.get("gender")
    if not gender:
        return jsonify({"message": Message.GENDER_REQUIRED.value}), 400

    gender = get_gender(gender)
    if not gender:
        return jsonify({"message": Message.INVALID_GENDER.value}), 400

    try:
        connection = connection_pool.getconn()
        if set_gender(connection, user_id, gender):
            return jsonify({"message": Message.GENDER_UPDATED.value}), 200
        return jsonify({"message": Message.INVALID_GENDER.value}), 400
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/birthday", methods=["PUT"])
def update_user_birthday_api(user_id: int):
    data = request.json
    birthday = data.get("birthday")
    if not birthday:
        return jsonify({"message": Message.BIRTHDAY_REQUIRED.value}), 400

    try:
        connection = connection_pool.getconn()
        if set_birthday(connection, user_id, birthday):
            return jsonify({"message": Message.BIRTHDAY_UPDATED.value}), 200
        return jsonify({"message": Message.INVALID_BIRTHDAY.value}), 400
    finally:
        connection_pool.putconn(connection)


@app.route("/login", methods=["POST"])
def try_login():
    data = request.json
    admin_login = data.get("login")
    admin_password = data.get("password")

    try:
        connection = connection_pool.getconn()
        result = check_admin_exists(connection, admin_login, admin_password)
        if (result):
            return jsonify({"auth": True})
        else:
            return jsonify({"auth": False, "error": "INVALID_LOGIN"})
    finally:
        connection_pool.putconn(connection)

@app.route("/register_admin", methods=["POST"])
def insert_admin():
    data = request.json
    admin_login = data.get("login")
    admin_password = data.get("password")

    try:
        connection = connection_pool.getconn()
        insert_admin_record(connection, admin_login, admin_password)
        return jsonify({})
    finally:
        connection_pool.putconn(connection)

@app.route("/event", methods=["POST"])
def insert_event():
    data = request.json
    name = data.get("title")
    description = data.get("description")
    start = data.get("range")[0]
    end = data.get("range")[1]
    category = data.get("category").get("id")
    sale = data.get("sale")

    try:
        connection = connection_pool.getconn()
        result = insert_event_record(connection, name, description, start, end, category, sale)
        broadcast_event(connection, name, description, start, end, category, sale)
        return jsonify({"result": result})
    finally:
        connection_pool.putconn(connection)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    app.run(host=args.host, debug=args.debug, load_dotenv=True)
