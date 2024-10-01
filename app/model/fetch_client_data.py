"""
This module provides functions to connect to a MySQL database, create tables, and fetch client data.

Functions:
- connect(): Connect to the MySQL database.
"""

import pymysql
from connect import connect_to_mysql_db

connection = connect_to_mysql_db()

def fetch_client_data(client_name):
    """
    Fetch client data based on the client name.
    
    Args:
        client_name (str): Name of the client.
    
    Returns:
        list: List of dictionaries containing client data.
    """
    try:
        conn = connect_to_mysql_db()
        if conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT client_id, api_secret, client_name, api_key
                    FROM client
                    WHERE client_name = %s
                """
                cursor.execute(query, (client_name,))
                rows = cursor.fetchall()
                return rows
    except pymysql.MySQLError as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
