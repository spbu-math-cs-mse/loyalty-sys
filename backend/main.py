import argparse
from datetime import datetime
from flask import Flask, request, jsonify
import hashlib
from message import Message

app = Flask(__name__)

def generate_user_id(chat_id: str) -> str:
    return hashlib.sha256(chat_id.encode()).hexdigest()

def validate_date(date_str: str) -> True:
    if date_str is None:
        return True
    date_format = "%Y-%m"
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    chat_id = data.get('chat_id')

    if not chat_id:
        return jsonify({"message": Message.CHAT_ID_REQUIRED.value}), 400
    
    # TODO for @vsdmitri: here should be some logic for creating user in db, remove the stub after implementation
    user_id = generate_user_id(chat_id)
    
    return jsonify({"message": Message.USER_CREATED.value, "user_id": user_id}), 201


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    # TODO for @vsdmitri: here should get some user data from db, remove the stub after implementation
    return jsonify({"username": "JohnDoe"})


@app.route('/user/<int:user_id>/purchase', methods=['POST'])
def record_purchase(user_id: int):
    data = request.json
    purchases_list = data.get('purchases', [])

    if not purchases_list:
        return jsonify({"message": Message.NO_PURCHASES_PROVIDED.value}), 400

    # TODO for @vsdmitri: here should be some logic for writing data to the db 
    # (you can change json format if you want, but please mention the change in the readme), 
    # remove the stub after implementation
    for item in purchases_list:
        product_id = item.get('product_id')
        quantity = item.get('quantity')

        if product_id is None or quantity is None:
            return jsonify({"message": Message.INVALID_PURCHASE_DATA.value}), 400

    return jsonify({"message": Message.PURCHASES_RECORDED.value, "user_id": user_id})


@app.route('/data/values', methods=['GET'])
def get_product_values():
    product_id = request.args.get('product_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date') 

    if product_id is None:
        return jsonify({"message": Message.PRODUCT_ID_REQUIRED.value}), 400

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    # TODO for @vsdmitri: here should be some logic for getting data from the db, remove the stub after implementation
    return jsonify({"label": "Milk", "values": [5, 6, 7]})


@app.route('/data/total_purchases', methods=['GET'])
def get_total_purchases():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400
  
    # TODO for @vsdmitri: here should be some logic for getting data from the db, remove the stub after implementation
    return jsonify({"total_purchases": 190300.0})


@app.route('/data/average_check', methods=['GET'])
def get_average_check():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400
    
    # TODO for @vsdmitri: here should be some logic for getting data from the db, remove the stub after implementation
    return jsonify({"average_check": 2500.0})


@app.route('/data/visitor_count', methods=['GET'])
def get_visitor_count():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not validate_date(start_date) or not validate_date(end_date):
        return jsonify({"message": Message.INVALID_DATE_FORMAT.value}), 400

    # TODO for @vsdmitri: here should be some logic for getting data from the db, remove the stub after implementation
    return jsonify({"visitor_count": 100})


@app.route('/data/products', methods=['GET'])
def get_products():
    # TODO for @vsdmitri: here should be some logic for getting data from the db, remove the stub after implementation
    return jsonify([{"id": 1, "name": "Milk"}, {"id": 2, "name": "Bread"}])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    app.run(host=args.host, debug=args.debug)
