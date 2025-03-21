import os
import secrets
import datetime

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
