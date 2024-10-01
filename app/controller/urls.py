"""
This module defines Flask blueprints and routes for credentials and tokens.
It registers endpoints for generating credentials and requesting access tokens using
Flask Blueprints (`credentials_blueprint` and `tokens_blueprint`).
"""

from flask import Blueprint
from controller.credentials import credentials_bp
from controller.tokens import tokens_bp

# Create Blueprints
credentials_blueprint = Blueprint('credentials', __name__)
tokens_blueprint = Blueprint('tokens', __name__)


@credentials_blueprint.route('/api/generate_credentials', methods=['POST'])
def handle_generate_credentials():
    """
    Route handler for generating client credentials.
    """
    from controller.credentials import generate_credentials
    return generate_credentials()

@tokens_blueprint.route('/api/request_access_token', methods=['POST'])
def handle_request_access_token():
    """
    Route handler for requesting access tokens.
    """
    from controller.tokens import request_access_token
    return request_access_token()

# Export blueprints
credentials_bp = credentials_blueprint
tokens_bp = tokens_blueprint
