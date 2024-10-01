"""
This module provides functions to connect to a MySQL database, create tables, and fetch client data.

Functions:
- connect(): Connect to the MySQL database.
"""
import pymysql
from model.connect import connect_to_mysql_db

conn = connect_to_mysql_db()

def create_client_table(connection):
    """
    Create the 'client' table if it does not exist.
    
    Args:
        connection (pymysql.connections.Connection): Database connection object.
    """
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS client (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        client_id VARCHAR(20) UNIQUE NOT NULL,
                        api_secret VARCHAR(255) NOT NULL,
                        api_key VARCHAR(24) UNIQUE NOT NULL,
                        client_name VARCHAR(100) NOT NULL,
                        UNIQUE KEY unique_client_id (client_id),
                        UNIQUE KEY unique_api_key (api_key)
                    )
                """)
                connection.commit()
                print("Client table created or already exists")
        except pymysql.MySQLError as e:
            print(f"Error creating 'client' table: {e}")
