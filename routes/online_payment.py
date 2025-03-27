from datetime import datetime
from flask import Blueprint, request, jsonify
from pymongo import MongoClient

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["payment_database"]
payment_collection = db["online_payments"]

class OnlinePayment:
    def __init__(self, transaction_id, name, amount, payment_method, payment_date):
        self.transaction_id = transaction_id
        self.name = name
        self.amount = amount
        self.payment_method = payment_method
        self.payment_date = payment_date

    def to_dict(self):
        """ Convert the object data to a dictionary for MongoDB storage """
        return {
            "transaction_id": self.transaction_id,
            "name": self.name,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_date": self.payment_date
        }

    def save_to_db(self):
        """ Save the payment record to MongoDB """
        try:
            payment_collection.insert_one(self.to_dict())
            return {"message": "Payment recorded successfully!"}, 201
        except Exception as e:
            return {"error": "Database error", "details": str(e)}, 500

# Flask Blueprint for Online Payments API
payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/submit-payment', methods=['POST'])
def submit_online_payment():
    """ API to handle online payment submission """
    data = request.json

    # Validate required fields
    required_fields = ["transaction_id", "name", "amount", "payment_method"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Add current date/time
    data["payment_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create an object and save to DB
    payment = OnlinePayment(**data)
    response, status = payment.save_to_db()

    return jsonify(response), status

@payment_bp.route('/print-receipt/<transaction_id>', methods=['GET'])
def print_receipt(transaction_id):
    """ API to retrieve and print payment receipt details """
    receipt_data = payment_collection.find_one({"transaction_id": transaction_id}, {"_id": 0})

    if receipt_data:
        return jsonify(receipt_data), 200

    return jsonify({"error": "Receipt not found"}), 404

@payment_bp.route('/search-payment/<name>', methods=['GET'])
def search_payment_by_name(name):
    """ API to search payments by user name """
    payment_records = list(payment_collection.find({"name": name}, {"_id": 0}))

    if payment_records:
        return jsonify({"records": payment_records}), 200

    return jsonify({"error": "No payments found for this name"}), 404