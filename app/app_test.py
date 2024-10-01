
"""
Unit tests for testing Flask application endpoints.
"""

import unittest
from app_server import app, generate_jwt

class TestFlaskApp(unittest.TestCase):
    """
    Test case for Flask application endpoints.
    """

    def setUp(self):
        """
        Set up the Flask test client.
        """
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_credentials_and_request_access_token(self):
        """
        Test case for generating credentials and requesting access token.
        """
        # Generate client credentials
        response = self.app.post(
            '/api/generate_credentials',
            json={'client_name': 'tony_stark'}
        )
        print('----------------------------------------------------------------------')
        print(f"Response status code: {response.status_code}")
        # print(f"Response data: {response.json}")

        response_data = response.get_json()

        if response.status_code == 200 and response_data['message'] == 'Client already exists':
            print("Client already exists, using existing credentials...")
            print('----------------------------------------------------------------------')
            client_details = response_data['client_details']
            client_id = client_details['client_id']
            api_secret = client_details['api_secret']
            api_key = client_details['api_key']
            print(f"Request from client_id : {client_id}")
            # print(f"api_secret: {api_secret}")
            # print(f"api_key: {api_key}")
        elif response.status_code == 201 and response_data['message'] == 'Client created successfully':
            print("Client credentials generated successfully...")
            print('----------------------------------------------------------------------')
            client_details = response_data['client_details']
            client_id = client_details['client_id']
            api_secret = client_details['api_secret']
            api_key = client_details['api_key']
            print(f"Generated client_id: {client_id}")
            # print(f"Generated api_secret: {api_secret}")
            # print(f"Generated api_key: {api_key}")
        else:
            self.fail(f"Unexpected response status code: {response.status_code}")

        # Generate JWT token
        jwt_token = generate_jwt(api_key, api_secret)
        print('\n',f"Generated jwt_token: {jwt_token}")
        access_token_response = self.app.post(
        '/api/request_access_token',
        json={'client_id': client_id, 'jwt_token': jwt_token}
    )
        self.assertEqual(access_token_response.status_code, 200,
                         f"Expected 200, but got {access_token_response.status_code}")
        access_token = access_token_response.json['access_token']
        print(f" access_token: {access_token}")
        # Access protected endpoint using the access token and client ID
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-ID': client_id
        }
        response = self.app.get('/api/data', headers=headers)
        self.assertEqual(response.status_code, 200, f"Expected 200, but {response.status_code}")
        print('\n',f"Protected API response: {response.json}")

if __name__ == '__main__':
    unittest.main()
