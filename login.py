from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import datetime 
import os
import secrets

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for mobile apps

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

jwt = JWTManager(app)

# MongoDB Setup
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"

try:
    mongo = PyMongo(app)
    users_collection = mongo.db.users  # Collection reference
except Exception as e:
    print("Error connecting to MongoDB:", str(e))

# ---------------- API Routes ---------------- #

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Flask API!"})

# User Registration (POST)
@app.route('/auth/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if users_collection.find_one({'username': username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    try:
        users_collection.insert_one({'username': username, 'password': hashed_password})
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# User Login (POST) - Returns JWT in JSON
@app.route('/auth/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify({"message": "Login successful", "access_token": access_token}), 200

    return jsonify({"error": "Invalid username or password"}), 401

# User Dashboard (GET - Protected)
@app.route('/user/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome {current_user}!"}), 200

# User Logout (POST) - Token should be removed on client side
@app.route('/auth/logout', methods=['POST'])
def logout_user():
    return jsonify({"message": "Logout successful. Please remove token on the client side."}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)