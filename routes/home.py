from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pymongo import PyMongo

home_bp = Blueprint('home', __name__)

# Sample services with URLs
services_data = {
    "water-bill": "/services/water-bill",
    "garbage-collection": "/services/garbage-collection",
    "property-tax": "/services/property-tax",
    "road-maintenance": "/services/road-maintenance",
    "public-transport": "/services/public-transport",
    "drainage-report": "/services/drainage-report",
    "birth-certificate": "/services/birth-certificate",
    "death-certificate": "/services/death-certificate",
    "complaints": "/services/complaints",
    "civic-center": "/services/civic-center",
    "shop-and-establishments": "/services/shop-and-establishments",
    "search-property": "/services/search-property",
    "recruitment": "/services/recruitment"
}

@home_bp.route('/', methods=['GET'])
def home():
    """ List available services. """
    return jsonify({"services": list(services_data.keys())}), 200

@home_bp.route('/service/<service_name>', methods=['GET'])
def get_service_url(service_name):
    """ Returns the service URL as JSON instead of redirecting. """
    if service_name in services_data:
        return jsonify({"service": service_name, "url": services_data[service_name]}), 200
    
    return jsonify({"error": "Service not found"}), 404

@home_bp.route('/search', methods=['GET'])
def search_service():
    """ Search for services by keyword. """
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Please provide a search query."}), 400

    matching_services = {service: url for service, url in services_data.items() if query in service}
    
    if matching_services:
        return jsonify({"matching_services": matching_services}), 200
    
    return jsonify({"error": "No matching service found"}), 404

@home_bp.route("/menu", methods=["GET"])
@jwt_required()  # Ensure user is authenticated
def menu():
    """ Returns the menu items along with user details """
    from app import mongo  # Avoid circular imports
    
    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": user_id}, {"_id": 0})  # Fetch user info
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    menu_items = [
        {"name": "Home", "route": "/home"},
        {"name": "Profile", "route": "/profile"},
        {"name": "Notifications", "route": "/notifications"},
        {"name": "Recent Transactions", "route": "/transactions"},
        {"name": "Tools", "route": "/tools"},
        {"name": "Settings", "route": "/settings"},
        {"name": "Privacy Policy", "route": "/privacy"},
        {"name": "Logout", "route": "/logout"}
    ]
    
    return jsonify(user=user, menu=menu_items), 200
