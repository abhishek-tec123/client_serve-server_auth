"""
This module provides functions to connect to a MySQL database, create tables, and fetch client data.

Functions:
- connect(): Connect to the MySQL database.
"""

import pymysql
from model.connect import connect_to_mysql_db


conn = connect_to_mysql_db()

def create_access_tokens(connection):
    """
    Create the 'access_tokens' table if it does not exist.
    
    Args:
        connection (pymysql.connections.Connection): Database connection object.
    """
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS access_tokens (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        token VARCHAR(255) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expiry_date TIMESTAMP NOT NULL,
                        reference_id INT,
                        FOREIGN KEY (reference_id) REFERENCES client(id)
                    )
                    DEFAULT CHARACTER SET = utf8mb4
                    DEFAULT COLLATE = utf8mb4_unicode_ci
                """)
                connection.commit()
                print("access_tokens table created or already exists")
        except pymysql.MySQLError as e:
            print(f"Error creating 'access_tokens' table: {e}")
