from datetime import datetime
from flask import Blueprint, request, jsonify
from pymongo import MongoClient

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["tax_database"]
tax_collection = db["professional_tax"]

class ProfessionalTaxPayment:
    def __init__(self, receipt_no, registration_no, firm_name, address, mobile_no, receipt_date, payable_tax_amount, selected_amount):
        self.receipt_no = receipt_no
        self.registration_no = registration_no
        self.firm_name = firm_name
        self.address = address
        self.mobile_no = mobile_no
        self.receipt_date = receipt_date
        self.payable_tax_amount = payable_tax_amount
        self.selected_amount = selected_amount

    def to_dict(self):
        """ Convert the object data to a dictionary for MongoDB storage """
        return {
            "receipt_no": self.receipt_no,
            "registration_no": self.registration_no,
            "firm_name": self.firm_name,
            "address": self.address,
            "mobile_no": self.mobile_no,
            "receipt_date": self.receipt_date,
            "payable_tax_amount": self.payable_tax_amount,
            "selected_amount": self.selected_amount
        }

    def save_to_db(self):
        """ Save the tax payment record to MongoDB """
        try:
            tax_collection.insert_one(self.to_dict())
            return {"message": "Tax payment record saved successfully!"}, 201
        except Exception as e:
            return {"error": "Database error", "details": str(e)}, 500

# Flask Blueprint for API routes
tax_bp = Blueprint('tax', __name__)

@tax_bp.route('/submit-tax', methods=['POST'])
def submit_tax_payment():
    """ API to handle tax payment submission """
    data = request.json

    # Validate required fields
    required_fields = ["receipt_no", "registration_no", "firm_name", "address", "mobile_no", "receipt_date", "payable_tax_amount", "selected_amount"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Create an object and save to DB
    tax_payment = ProfessionalTaxPayment(**data)
    response, status = tax_payment.save_to_db()

    return jsonify(response), status

@tax_bp.route('/print-receipt/<receipt_no>', methods=['GET'])
def print_receipt(receipt_no):
    """ API to retrieve and print tax receipt details """
    receipt_data = tax_collection.find_one({"receipt_no": receipt_no}, {"_id": 0})

    if receipt_data:
        return jsonify(receipt_data), 200

    return jsonify({"error": "Receipt not found"}), 404

@tax_bp.route('/search-registration/<registration_no>', methods=['GET'])
def search_by_registration_no(registration_no):
    """ API to search tax payment by registration number """
    tax_records = list(tax_collection.find({"registration_no": registration_no}, {"_id": 0}))

    if tax_records:
        return jsonify({"records": tax_records}), 200

    return jsonify({"error": "No records found for this registration number"}), 404