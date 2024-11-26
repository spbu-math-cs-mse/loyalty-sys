import argparse
from datetime import datetime

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
    get_average_purchase,
    get_visits_count,
    get_all_products,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app)

connection_pool = None


with app.app_context():
    connection_pool = get_connections_pool()


def validate_date(date_str: str) -> bool:
    if date_str is None:
        return True
    date_format = "%Y-%m"
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False
# TODO: Structurize and store in the database in parts, not in whole
'''
privileges JSON example:
{
  percent: {
    settings: {
      active: false,
      levels: 5,
    },
    privileges: [
      {
        id: "AS765HGJAL",
        label: "Bronze",
        sale: {
          all: 5,
        },
        starts_from: 0,
      },
      {
        id: "AS76AHGJAL",
        label: "Silver",
        sale: {
          all: 15,
        },
        starts_from: 2000,
      },
      {
        id: "BS765HGJAL",
        label: "Golden",
        sale: {
          all: 25,
        },
        starts_from: 5000,
      },
    ],
  },
  point: {
    settings: {
      active: false,
      levels: 15,
    },
    privileges: [
      {
        id: "1S765HGJAL",
        label: "Bronze",
        sale: {
          all: 0.5,
        },
        starts_from: 0,
      },
    ],
  },
}
'''

@app.route("/privileges", methods=["GET"])
def get_privileges():
    privileges = {}  # TODO: implement database function
    return jsonify(discount), 200


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
    discount = {"type": "процент", "value": "10"}  # TODO: implement database function
    return jsonify(discount)


@app.route("/user/<int:user_id>/total_purchases", methods=["GET"])
def get_user_total_purchases_api(user_id: int):
    total_purchases = 1000.0  # TODO: implement database function
    return jsonify({"total_purchases": total_purchases})


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
    # TODO: update gender in database
    return jsonify({"message": Message.GENDER_UPDATED.value})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    app.run(host=args.host, debug=args.debug, load_dotenv=True)
