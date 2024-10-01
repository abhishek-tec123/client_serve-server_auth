# without jwt token--------------------------------------------------------------------------------------------------------------------------------


# """
# This module implements the handler for generating client credentials.
# """

# import secrets
# from flask import request, jsonify,Blueprint
# from utils import require_json, generate_client_id, generate_api_key
# from views.db_connection import get_connection
# import pymysql

# credentials_bp = Blueprint('credentials', __name__)
# conn = get_connection()

# @require_json
# def generate_credentials():
#     """Generate client credentials and store in the database."""
#     data = request.json
#     client_name = data.get('client_name')

#     if conn:
#         cursor = None
#         try:
#             cursor = conn.cursor(pymysql.cursors.DictCursor)
#             cursor.execute(
#                 "SELECT * FROM client WHERE client_name = %s", 
#                 (client_name,)
#             )
#             existing_client = cursor.fetchone()

#             if existing_client:
#                 return jsonify({
#                     'message': 'Client already exists',
#                     'client_details': {
#                         'client_id': existing_client['client_id'],
#                         'api_secret': existing_client['api_secret'],
#                         'api_key': existing_client['api_key']
#                     }
#                 }), 200

#             client_id = generate_client_id()
#             api_secret = secrets.token_urlsafe(32)
#             api_key = generate_api_key(client_id, api_secret)

#             cursor.execute(
#                 "INSERT INTO client (client_id, api_secret, api_key, client_name) "
#                 "VALUES (%s, %s, %s, %s)",
#                 (client_id, api_secret, api_key, client_name)
#             )
#             conn.commit()

#             return jsonify({
#                 'client_id': client_id,
#                 'api_secret': api_secret,
#                 'api_key': api_key,
#                 'client_name': client_name
#             }), 201

#         except pymysql.MySQLError as e:
#             print(f"Error inserting data: {e}")
#             return jsonify({'error': 'Internal Server Error'}), 500
#         finally:
#             if cursor:
#                 cursor.close()
#     else:
#         return jsonify({'error': 'Database connection error'}), 500

# with jwt token--------------------------------------------------------------------------------------------------------------------------------

import secrets
from flask import request, jsonify, Blueprint
from utils import require_json, generate_client_id, generate_api_key, generate_jwt
from views.db_connection import get_connection
import pymysql

credentials_bp = Blueprint('credentials', __name__)
conn = get_connection()

@require_json
def generate_credentials():
    """Generate client credentials and store in the database."""
    data = request.json
    client_name = data.get('client_name')

    if conn:
        cursor = None
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM client WHERE client_name = %s", 
                (client_name,)
            )
            existing_client = cursor.fetchone()

            if existing_client:
                jwt_token = generate_jwt(existing_client['api_key'], existing_client['api_secret'])
                response = {
                    'client_details': {
                        'client_id': existing_client['client_id'],
                        'api_secret': existing_client['api_secret'],
                        'api_key': existing_client['api_key']
                    },
                    'jwt_token': jwt_token,
                    'message': 'Client already exists'
                }
                return jsonify(response), 200

            client_id = generate_client_id()
            api_secret = secrets.token_urlsafe(32)
            api_key = generate_api_key(client_id, api_secret)
            jwt_token = generate_jwt(client_id, api_secret)

            cursor.execute(
                "INSERT INTO client (client_id, api_secret, api_key, client_name) "
                "VALUES (%s, %s, %s, %s)",
                (client_id, api_secret, api_key, client_name)
            )
            conn.commit()

            response = {
                'client_details': {
                    'client_id': client_id,
                    'api_secret': api_secret,
                    'api_key': api_key
                },
                'jwt_token': jwt_token,
                'message': 'Client created successfully'
            }

            return jsonify(response), 201

        except pymysql.MySQLError as e:
            print(f"Error inserting data: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            if cursor:
                cursor.close()
    else:
        return jsonify({'error': 'Database connection error'}), 500
