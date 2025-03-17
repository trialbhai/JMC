from flask import Blueprint, jsonify, request, redirect

home_bp = Blueprint('home', __name__)

# Sample services with redirection URLs
services_data = {
    "water-bill": "/services/water-bill",
    "garbage-collection": "/services/garbage-collection",
    "property-tax": "/services/property-tax",
    "road-maintenance": "/services/road-maintenance",
    "public-transport": "/services/public-transport",
    "drainage-report": "/services/drainage-report"
}

@home_bp.route('/', methods=['GET'])
def home():
    """ List available services. """
    return jsonify({"services": list(services_data.keys())}), 200

@home_bp.route('/service/<service_name>', methods=['GET'])
def redirect_service(service_name):
    """ Redirects to a specific service page. """
    if service_name in services_data:
        return redirect(services_data[service_name])
    
    return jsonify({"error": "Service not found"}), 404

@home_bp.route('/search', methods=['GET'])
def search_service():
    """ Search for services by keyword. """
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Please provide a search query."}), 400

    matching_services = [service for service in services_data.keys() if query in service]
    return jsonify({"matching_services": matching_services}) if matching_services else jsonify({"error": "No matching service found"}), 404
