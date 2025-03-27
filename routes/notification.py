import datetime
import random
from flask import Blueprint, jsonify, request

# Define Blueprint
notification_bp = Blueprint("notifications", __name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
# Sample services and templates
SERVICES = [
    {"type": "Water Bill", "template": "Dear {name}, your {type} of ${amount} is due by {due_date}."},
    {"type": "Electricity Bill", "template": "Reminder: Your {type} of ${amount} is pending. Pay before {due_date}."},
    {"type": "Property Tax", "template": "Hello {name}, your {type} is due soon. Amount: ${amount}. Due Date: {due_date}."},
    {"type": "Traffic Fine", "template": "You have a {type} of ${amount}. Clear it by {due_date} to avoid penalties."},
    {"type": "Garbage Collection Fee", "template": "Your {type} for this month is ${amount}. Pay by {due_date}."}
]

def generate_random_due_date():
    """Generate a random due date between 5 to 15 days from today."""
    return (datetime.datetime.now() + datetime.timedelta(days=random.randint(5, 15))).strftime("%B %d, %Y")

def generate_random_amount():
    """Generate a random bill amount between $50 and $500."""
    return random.randint(50, 500)

def generate_dynamic_notification(user_name):
    """Generates a dynamic notification for a user."""
    selected_service = random.choice(SERVICES)  # Pick a random service
    due_amount = generate_random_amount()  # Generate a random amount
    due_date = generate_random_due_date()  # Generate a random due date

    # Format message dynamically
    message = selected_service["template"].format(
        name=user_name,
        type=selected_service["type"],
        amount=due_amount,
        due_date=due_date
    )

    # Create notification object
    notification = {
        "user_name": user_name,
        "title": f"{selected_service['type']} Due Reminder",
        "message": message,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return notification

@notification_bp.route("/generate", methods=["GET"])
def get_notification():
    """API endpoint to generate a test notification."""
    user_name = request.args.get("name", "User")  # Default to "User" if no name provided
    notification = generate_dynamic_notification(user_name)
    return jsonify(notification), 200
