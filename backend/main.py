import argparse

from flask import Flask, request, jsonify
from flask_cors import CORS
from message import Message

from postgress.common import (
    find_or_create_user,
    get_connections_pool,
    insert_purchase,
    insert_purchase_info,
    get_product_statistic,
    get_purchases_count,
    get_user_discount,
    get_average_purchase,
    get_visits_count,
    get_all_products,
    set_gender,
    set_user_discount,
)

from utils import validate_date, get_gender, get_discount_type

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app)

connection_pool = None


with app.app_context():
    connection_pool = get_connections_pool()

@app.route("/privileges", methods=["GET"])
def get_privileges():
    privileges = {}  # TODO: implement database function
    return jsonify(privileges), 200


@app.route("/privileges", methods=["POST"])
def send_privileges():
    data = request.json  # TODO: implement database function
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
        result = get_purchases_count(connection, start_date, end_date)
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


@app.route("/data/visitor_count", methods=["GET"])
def get_visitor_count():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_visits_count(connection, start_date, end_date)
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
                for id, label, price in result
            ]
        )
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/discount", methods=["GET"])
def get_user_discount_api(user_id: int):
    try:
        connection = connection_pool.getconn()
        result = get_user_discount(connection, user_id)

        if result is None:
            return (
                jsonify({"type": "no discount yet", "value": None}),
                200,
            )

        discount_type, level = result

        return (
            jsonify({"type": discount_type, "value": level}),
            200,
        )
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/discount", methods=["PUT"])
def set_user_discount_api(user_id: int):
    try:
        connection = connection_pool.getconn()
        discount_id = request.json.get("discount_id")
        if not discount_id:
            return jsonify({"message": Message.NO_DISCOUNT.value}), 400

        result = set_user_discount(connection, user_id, discount_id)

        if result is None:
            return jsonify({"message": Message.INVALID_DISCOUNT.value}), 400

        return jsonify({"message": Message.DISCOUNT_UPDATED.value}), 200
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/total_purchases", methods=["GET"])
def get_user_total_purchases_api(user_id: int):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    try:
        connection = connection_pool.getconn()
        result = get_purchases_count(connection, start_date, end_date, user_id)
        return jsonify({"total_purchases": result})
    finally:
        connection_pool.putconn(connection)


@app.route("/user/<int:user_id>/loyalty_level", methods=["GET"])
def get_user_loyalty_level_api(user_id: int):
    loyalty_level = "Серебряный"  # TODO: implement database function
    return jsonify({"loyalty_level": loyalty_level})


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

    # TODO: implement handling birthday in database
    return jsonify(f"ok for {user_id}"), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    app.run(host=args.host, debug=args.debug, load_dotenv=True)
