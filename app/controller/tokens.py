"""
This module implements the handler for generating access tokens.
"""

import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, Blueprint
from utils import require_json, verify_jwt, get_ist_time
from views.db_connection import get_connection
import pymysql

tokens_bp = Blueprint('tokens', __name__)
conn = get_connection()

@require_json
def request_access_token():
    """Generate an access token for the given client credentials."""
    data = request.json
    client_id = data.get('client_id')
    jwt_token = data.get('jwt_token')

    if conn:
        cursor = None
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM client WHERE client_id = %s", 
                (client_id,)
            )
            client_record = cursor.fetchone()
            print(client_record['api_key'])

            if not client_record:
                return jsonify({'error': 'Client ID not found'}), 404

            api_secret = client_record['api_secret']
            payload = verify_jwt(jwt_token, api_secret)
            if not payload:
                return jsonify({'error': 'Invalid or expired JWT token'}), 401

            api_key = payload.get('api_key')

            if not api_key:
                return jsonify({'error': 'API key not found in JWT token'}), 401

            if not payload:
                return jsonify({'error': 'Invalid or expired JWT token'}), 401

            api_key = payload.get('api_key')
            print('api_key:', api_key)

            if client_record['api_key'] != api_key:
                return jsonify({'error': 'Invalid credentials'}), 401

            access_token = secrets.token_urlsafe(16)
            current_ist_time = get_ist_time()
            formatted_ist_time = current_ist_time.strftime('%Y-%m-%d %H:%M:%S')
            token_created_at = datetime.strptime(formatted_ist_time, '%Y-%m-%d %H:%M:%S')
            token_expiry_date = token_created_at + timedelta(minutes=1)
            cursor.execute(
                "INSERT INTO access_tokens (token, created_at, expiry_date, reference_id) "
                "VALUES (%s, %s, %s, %s)",
                (access_token, token_created_at, token_expiry_date, client_record['id'])
            )
            conn.commit()

            return jsonify({'access_token': access_token}), 200

        except pymysql.MySQLError as e:
            print(f"Error inserting access token: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            if cursor:
                cursor.close()
    else:
        return jsonify({'error': 'Database connection error'}), 500
