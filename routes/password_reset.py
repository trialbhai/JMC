from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import datetime
import os
import secrets

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Autho        adb reverse tcp:5000 tcp:5000rization"]
    }
})
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

jwt = JWTManager(app)

# MongoDB Setup
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"

try:
    mongo = PyMongo(app)
    users_collection = mongo.db.users  # Collection reference
    users_collection.create_index("phone", unique=True)  # Ensure unique phone numbers
except Exception as e:
    print("Error connecting to MongoDB:", str(e))

# ---------------- API Routes ---------------- #

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Flask API!"})

# User Registration (POST)
@app.route('/signup', methods=['POST'])
def register_user():
    data = request.json
    name = data.get('name')
    phone = data.get('phoneNumber')
    password = data.get('password')
    role = data.get('role')

    # Validate required fields
    if not all([name, phone, password, role]):
        return jsonify({"error": "All fields are required"}), 400

    # Validate role
    allowed_roles = ['citizen', 'architect_engineer', 'employee', 'vehicle_dealer']
    if role not in allowed_roles:
        return jsonify({"error": "Invalid role specified"}), 400

    # Check existing user
    if users_collection.find_one({'phone': phone}):
        return jsonify({"error": "User already exists"}), 400

    # Create new user
    try:
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            'name': name,
            'phone': phone,
            'password': hashed_password,
            'role': role
        })
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Login (POST)
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    phone = data.get('phoneNumber')
    password = data.get('password')

    user = users_collection.find_one({'phone': phone})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Include role in JWT and response
    access_token = create_access_token(identity={
        "phone": phone,
        "name": user["name"],
        "role": user["role"]
    })
    
    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": {
            "name": user["name"],
            "phone": phone,
            "role": user["role"]
        }
    }), 200

# User Dashboard (GET - Protected)
@app.route('/user/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome {current_user['name']}!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)