from models.user import User
from utils.security import hash_password, check_password
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(data):
        if not data.get("username") or not data.get("password"):
            return {"error": "Username and password required", "status": 400}

        if User.find_by_username(data["username"]):
            return {"error": "User already exists", "status": 409}

        hashed_password = hash_password(data["password"])
        User.create_user({"username": data["username"], "password": hashed_password})
        return {"message": "User registered successfully", "status": 201}

    @staticmethod
    def login_user(data):
        user = User.find_by_username(data["username"])
        if not user or not check_password(user["password"], data["password"]):
            return {"error": "Invalid credentials", "status": 401}

        access_token = create_access_token(identity=data["username"])
        return {"message": "Login successful", "access_token": access_token, "status": 200}
