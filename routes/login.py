from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity
from services.auth_service import AuthService
from cryptography.fernet import Fernet
import os

# Ensure TOKEN_ENCRYPTION_KEY is set persistently
TOKEN_ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY")
if not TOKEN_ENCRYPTION_KEY:
    raise ValueError("TOKEN_ENCRYPTION_KEY must be set in environment variables.")

cipher = Fernet(TOKEN_ENCRYPTION_KEY.encode())

login_bp = Blueprint('login', __name__)

def set_auth_cookie(response, token):
    """
    Encrypts and sets the access token in a secure HTTP-only cookie.
    """
    encrypted_token = cipher.encrypt(token.encode()).decode()  # Encrypt JWT
    secure_cookie = os.getenv("FLASK_ENV", "production") == "production"
    response.set_cookie("access_token", encrypted_token, httponly=True, secure=secure_cookie, samesite="Lax")
    return response

def clear_auth_cookie(response):
    """
    Clears the authentication cookie by setting an expired value.
    """
    response.set_cookie("access_token", "", expires=0, httponly=True, secure=True, samesite="Lax")
    return response

def get_jwt_from_cookie():
    """
    Retrieves and decrypts the JWT token from the HTTP-only cookie.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        decrypted_token = cipher.decrypt(token.encode()).decode()
        return decrypted_token
    except:
        return None

@login_bp.route('/register', methods=['POST'])
def register_user():
    """ Register a new user """
    data = request.json
    response = AuthService.register_user(data)
    return jsonify(response), response.get("status", 400)

@login_bp.route('/login', methods=['POST'])
def login_user():
    """ User login - returns encrypted JWT in a secure cookie """
    data = request.json
    response = AuthService.login_user(data)

    if response.get("status") == 200:
        token = response["access_token"]
        resp = make_response(jsonify({"message": "Login successful"}))
        return set_auth_cookie(resp, token), 200

    return jsonify(response), response.get("status", 400)

@login_bp.route('/dashboard', methods=['GET'])
def user_dashboard():
    """ Protected user dashboard using JWT from cookies """
    token = get_jwt_from_cookie()
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    verify_jwt_in_request()  # Ensures JWT validation
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome {current_user}!"}), 200

@login_bp.route('/logout', methods=['POST'])
def logout_user():
    """ Logout user and remove authentication cookie """
    resp = make_response(jsonify({"message": "Logout successful"}))
    return clear_auth_cookie(resp), 200
