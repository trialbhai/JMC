from flask import Flask, jsonify, request, redirect, url_for

app = Flask(__name__)

# Sample services with redirection URLs
services_data = {
    "water-bill": "/services/water-bill",
    "garbage-collection": "/services/garbage-collection",
    "property-tax": "/services/property-tax",
    "road-maintenance": "/services/road-maintenance",
    "public-transport": "/services/public-transport",
    "drainage-report": "/services/drainage-report"
}

@app.route('/home', methods=['GET'])
def home():
    """
    Home route that lists available services.
    """
    return jsonify({"services": list(services_data.keys())}), 200

@app.route('/service/<service_name>', methods=['GET'])
def redirect_service(service_name):
    """
    Redirects to a specific service page.
    Example: /service/water-bill -> Redirects to /services/water-bill
    """
    if service_name in services_data:
        return redirect(services_data[service_name])
    
    return jsonify({"error": "Service not found"}), 404

@app.route('/search', methods=['GET'])
def search_service():
    """
    Search for services by keyword and return matching services.
    Example: /search?query=water
    """
    query = request.args.get('query', '').lower()

    if not query:
        return jsonify({"error": "Please provide a search query."}), 400

    matching_services = [service for service in services_data.keys() if query in service]

    if matching_services:
        return jsonify({"matching_services": matching_services}), 200

    return jsonify({"error": "No matching service found"}), 404

if __name__ == '__main__':
    app.run(debug=True)