import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv  # Load environment variables
from config import Config
from routes.home import home_bp
from routes.login import login_bp
from routes.professional_tax import tax_bp  # Import Professional Tax Routes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for mobile apps

# Load configuration
app.config.from_object(Config)

app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/your_database")
mongo = PyMongo(app)  # Initialize PyMongo


# Ensure essential environment variables are set
if not os.getenv("TOKEN_ENCRYPTION_KEY"):
    raise ValueError("TOKEN_ENCRYPTION_KEY must be set in environment variables.")

if not app.config.get("MONGO_URI"):
    raise ValueError("MONGO_URI is not set in Config")

# Initialize MongoDB
mongo = PyMongo(app)

# Initialize JWT
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(login_bp, url_prefix="/auth")
app.register_blueprint(tax_bp, url_prefix="/services/professional-tax")  # New route for tax payments

@app.route("/")
def health_check():
    """Health check route to verify server status"""
    return {"message": "Server is running!"}, 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
