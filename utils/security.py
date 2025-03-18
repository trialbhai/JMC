import re
from werkzeug.security import generate_password_hash, check_password_hash

def sanitize_input(input_string):
    sanitized_string = re.sub(r'[^a-zA-Z0-9@_.-]', '', input_string)
    return sanitized_string

def hash_password(password):
    sanitized_password = sanitize_input(password)
    return generate_password_hash(sanitized_password)

def check_password(hashed_password, plain_password):
    sanitized_password = sanitize_input(plain_password)
    return check_password_hash(hashed_password, sanitized_password)
