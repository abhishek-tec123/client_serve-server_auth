# -----------------------------------------------------------------------------------------
# for app test case automated take client name as input for test case generate credentials
# and get access token-------------------------------
# -----------------------------------------------------------------------------------------

"""
This module implements a Flask application for client authentication.
It includes endpoints for generating credentials and requesting access tokens.
"""

# import secrets
# from datetime import datetime, timedelta
# from functools import wraps
# import pymysql
# import scrypt
# import jwt
# from flask import Flask, request, jsonify
# from model import connect_to_mysql_db, create_client_table, create_access_tokens

# app = Flask(__name__)

# # Establish database connection and create table if it doesn't exist
# conn = connect_to_mysql_db()
# create_client_table(conn)
# create_access_tokens(conn)

# def get_ist_time():
#     """Get the current time in IST (Indian Standard Time) by adding the offset manually."""
#     utc_now = datetime.utcnow()
#     ist_offset = timedelta(hours=5, minutes=30)
#     ist_time = utc_now + ist_offset
#     return ist_time

# def generate_jwt(api_key, api_secret):
#     """Generate a JWT token for the given API key and secret."""
#     payload = {
#         'api_key': api_key,
#         'exp': datetime.utcnow() + timedelta(minutes=1)
#     }
#     token = jwt.encode(payload, api_secret, algorithm='HS256')
#     return token.decode('utf-8') if isinstance(token, bytes) else token

# def token_required(f):
#     """Decorator to ensure the request includes a valid token."""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization')

#         if not token:
#             return jsonify({'error': 'Token is missing!'}), 401

#         try:
#             token = token.split(" ")[1]  # Extract token from Bearer <token>
#             cursor = conn.cursor(pymysql.cursors.DictCursor)
#             cursor.execute("SELECT * FROM access_tokens WHERE token = %s", (token,))
#             access_token_record = cursor.fetchone()

#             if not access_token_record:
#                 return jsonify({'error': 'Invalid token!'}), 401

#             # Check token expiration
#             expiry_date = access_token_record['expiry_date']
#             current_ist_time = get_ist_time()

#             if current_ist_time >= expiry_date:
#                 return jsonify({'error': 'Token has expired!'}), 401

#             # Pass the reference ID to the wrapped function
#             kwargs['reference_id'] = access_token_record['reference_id']

#         except (pymysql.MySQLError, IndexError) as e:
#             print(f"Error verifying token: {e}")
#             return jsonify({'error': 'Internal Server Error'}), 500
#         finally:
#             cursor.close()

#         return f(*args, **kwargs)

#     return decorated

# def generate_client_id():
#     """Generate a random client ID."""
#     return secrets.token_urlsafe(10)

# def generate_api_key(client_id, api_secret):
#     """Generate a secure API key based on client ID and secret."""
#     combined_string = f"{client_id}{api_secret}"
#     hashed_token_bytes = scrypt.hash(
#         combined_string.encode(),
#         salt=secrets.token_bytes(32),
#         N=16384,
#         r=8,
#         p=1,
#         buflen=48,
#     )
#     hashed_token_hex = hashed_token_bytes.hex()
#     start_index = secrets.randbelow(len(hashed_token_hex) - 23)
#     random_token_hex = hashed_token_hex[start_index:start_index + 24]

#     api_key = f"ab_{random_token_hex}"
#     return api_key[:24]

# def verify_jwt(token, api_secret):
#     """Verify the given JWT token with the secret."""
#     try:
#         payload = jwt.decode(token, api_secret, algorithms=['HS256'])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None

# def require_json(f):
#     """Decorator to ensure JSON content-type."""
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if request.content_type != 'application/json':
#             return jsonify({'error': 'Content-Type must be application/json'}), 400
#         return f(*args, **kwargs)

#     return wrap

# @app.route('/api/generate_credentials', methods=['POST'])
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
#             app.logger.error("Error inserting data: %s", e)
#             return jsonify({'error': 'Internal Server Error'}), 500
#         finally:
#             if cursor:
#                 cursor.close()
#     else:
#         return jsonify({'error': 'Database connection error'}), 500

# @app.route('/api/request_access_token', methods=['POST'])
# @require_json
# def request_access_token():
#     """Generate an access token for the given client credentials."""
#     data = request.json
#     client_id = data.get('client_id')
#     jwt_token = data.get('jwt_token')

#     if conn:
#         cursor = None
#         try:
#             cursor = conn.cursor(pymysql.cursors.DictCursor)
#             cursor.execute(
#                 "SELECT * FROM client WHERE client_id = %s",
#                 (client_id,)
#             )
#             client_record = cursor.fetchone()

#             if not client_record:
#                 return jsonify({'error': 'Client ID not found'}), 404

#             api_secret = client_record['api_secret']
#             payload = verify_jwt(jwt_token, api_secret)

#             if not payload:
#                 return jsonify({'error': 'Invalid or expired JWT token'}), 401

#             api_key = payload.get('api_key')

#             if client_record['api_key'] != api_key:
#                 return jsonify({'error': 'Invalid credentials'}), 401

#             access_token = secrets.token_urlsafe(16)
#             current_ist_time = get_ist_time()
#             formatted_ist_time = current_ist_time.strftime('%Y-%m-%d %H:%M:%S')
#             token_created_at = datetime.strptime(formatted_ist_time, '%Y-%m-%d %H:%M:%S')
#             token_expiry_date = token_created_at + timedelta(minutes=1)
#             cursor.execute(
#                 "INSERT INTO access_tokens (token, created_at, expiry_date, reference_id) "
#                 "VALUES (%s, %s, %s, %s)",
#                 (access_token, token_created_at, token_expiry_date, client_record['id'])
#             )
#             conn.commit()

#             app.logger.info("Generated access token for client ID '%s'", client_id)
#             return jsonify({'access_token': access_token}), 200

#         except pymysql.MySQLError as e:
#             app.logger.error("Error inserting access token: %s", e)
#             return jsonify({'error': 'Internal Server Error'}), 500
#         finally:
#             if cursor:
#                 cursor.close()
#     else:
#         return jsonify({'error': 'Database connection error'}), 500

# qa_data = [
#     {
#         "question": "What is OAuth2.0?",
#         "answer": "OAuth2.0 is an authorization framework that allows third-party services."
#     }
# ]

# # @app.route('/api/data', methods=['GET'])
# # @token_required
# # def get_data(reference_id):
# #     """Protected endpoint that returns a greeting message."""
# #     return jsonify({"message": f"Hello, OAuth2.0 Client with reference ID {reference_id}!"})
# @app.route('/api/data', methods=['GET'])
# @token_required
# def get_data(reference_id):
#     """Protected endpoint that returns a greeting message and QA data."""
#     return jsonify({
#         "message": f"Hello, OAuth2.0 Client with reference ID {reference_id}!",
#         "qa_data": qa_data
#     })
# if __name__ == '__main__':
#     app.run(debug=True)



# import secrets
import os
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from controller.urls import credentials_bp, tokens_bp

from views.db_connection import get_connection
import pymysql
import jwt
from views.qa_model import answer_question_from_pdf_with_retry


app = Flask(__name__)

# Establish database connection and create table if it doesn't exist
conn = get_connection()


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

def token_required(f):
    """Decorator to ensure the request includes a valid token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            token = token.split(" ")[1]  # Extract token from Bearer <token>
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM access_tokens WHERE token = %s", (token,))
            access_token_record = cursor.fetchone()

            if not access_token_record:
                return jsonify({'error': 'Invalid token!'}), 401

            # Check token expiration
            expiry_date = access_token_record['expiry_date']
            current_ist_time = get_ist_time()

            if current_ist_time >= expiry_date:
                return jsonify({'error': 'Token has expired!'}), 401

            # Pass the reference ID to the wrapped function
            kwargs['reference_id'] = access_token_record['reference_id']

        except (pymysql.MySQLError, IndexError) as e:
            print(f"Error verifying token: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()

        return f(*args, **kwargs)

    return decorated

@app.route('/api/data', methods=['GET'])
# @token_required
def get_data():
    """Protected endpoint that returns QA data from PDF files."""
    docs_folder = "/Users/macbook/Desktop/llm-deployment_scrty/app/docs"
    qa_data = []

    for filename in os.listdir(docs_folder):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(docs_folder, filename)
            user_question = "what is iso"
            answer = answer_question_from_pdf_with_retry(pdf_file, user_question)
            qa_data.append({
                "file": filename,
                "question": user_question,
                "answer": answer
            })

    return jsonify({
        "message": f"Hello, Client with reference ID !",
        "qa_data": qa_data
    })

# Register Blueprints
app.register_blueprint(credentials_bp)
app.register_blueprint(tokens_bp)

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'hi testing application flask app'

if __name__ == '__main__':
    app.run(debug=True)
