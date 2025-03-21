from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import secrets

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/transactions"
app.config['JWT_SECRET_KEY'] = 'secrets.token_hex(32)'  # Change this to a strong secret key

mongo = PyMongo(app)
jwt = JWTManager(app)

# Create a Blueprint for transaction routes
transaction_bp = Blueprint('transaction', __name__)

# Add Transaction (Protected)
@transaction_bp.route('/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    user_id = get_jwt_identity()
    data = request.json
    transaction = {
        "user_id": user_id,
        "amount": data['amount'],
        "category": data['category'],
        "description": data.get('description', ''),
        "date": data['date']
    }
    mongo.db.transactions.insert_one(transaction)
    return jsonify({"message": "Transaction added successfully!"})

# Get Transactions (Protected)
@transaction_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = mongo.db.transactions.find({"user_id": user_id})
    transactions_list = [{
        "id": str(t["_id"]),
        "amount": t["amount"],
        "category": t["category"],
        "description": t["description"],
        "date": t["date"]
    } for t in transactions]
    return jsonify(transactions_list)

app.register_blueprint(transaction_bp)

if __name__ == '__main__':
    app.run(debug=True)