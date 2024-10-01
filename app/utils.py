"""
This module implements a Flask application for client authentication.
It includes endpoints for generating credentials.
"""
import secrets
from functools import wraps
from datetime import datetime, timedelta
import scrypt
from flask import request, jsonify
import jwt

def require_json(f):
    """Decorator to ensure JSON content-type."""
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.content_type != 'application/json':
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)

    return wrap

def generate_client_id():
    """Generate a random client ID."""
    return secrets.token_urlsafe(10)

def generate_api_key(client_id, api_secret):
    """Generate a secure API key based on client ID and secret."""
    combined_string = f"{client_id}{api_secret}"
    hashed_token_bytes = scrypt.hash(
        combined_string.encode(),
        salt=secrets.token_bytes(32),
        N=16384,
        r=8,
        p=1,
        buflen=48,
    )
    hashed_token_hex = hashed_token_bytes.hex()
    start_index = secrets.randbelow(len(hashed_token_hex) - 23)
    random_token_hex = hashed_token_hex[start_index:start_index + 24]

    api_key = f"ab_{random_token_hex}"
    return api_key[:24]


def verify_jwt(token, api_secret):
    """Verify the given JWT token with the secret."""
    try:
        payload = jwt.decode(token, api_secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_ist_time():
    """Get the current time in IST (Indian Standard Time) by adding the offset manually."""
    utc_now = datetime.utcnow()
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_now + ist_offset
    return ist_time


def generate_jwt(api_key, api_secret):
    """Generate a JWT token for the given API key and secret."""
    payload = {
        'api_key': api_key,
        'exp': datetime.utcnow() + timedelta(minutes=1)
    }
    token = jwt.encode(payload, api_secret, algorithm='HS256')
    return token.decode('utf-8') if isinstance(token, bytes) else token