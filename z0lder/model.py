
"""
This module provides functions to connect to a MySQL database, create tables, and fetch client data.

Functions:
- connect(): Connect to the MySQL database.
- connect_to_mysql_db(): Connect to the MySQL database and retrieve the database version.
- create_client_table(connection): Create the 'client' table if it does not exist.
- create_access_tokens(connection): Create the 'access_tokens' table if it does not exist.
- fetch_client_data(client_name): Fetch client data based on the client name.
- main(): Main function to create tables.
"""

import os
import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

load_dotenv()

# Retrieve the database credentials from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def connect():
    """
    Connect to the MySQL database using credentials from environment variables.
    
    Returns:
        connection (pymysql.connections.Connection): Database connection object if successful,
        else None.
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=DictCursor  # Optional: return rows as dictionaries
        )
        print("Connected to the database successfully!")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def connect_to_mysql_db():
    """
    Connect to the MySQL database and retrieve the database version.
    
    Returns:
        connection (pymysql.connections.Connection): Database connection object if successful,
        else None.
    """
    connection = connect()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL Database Version: {version['VERSION()']}")
            return connection  # Return the connection object if successful
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            connection.close()
            return None

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
        cursor = conn.cursor()
        query = """
            SELECT client_id, api_secret, client_name, api_key
            FROM client
            WHERE client_name = %s
        """
        cursor.execute(query, (client_name,))
        rows = cursor.fetchall()
        return rows
    except pymysql.Error as error:
        print(f"Error fetching data: {error}")
        return None
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def main():
    """
    Main function to create tables.
    """
    connection = connect_to_mysql_db()
    if connection:
        create_client_table(connection)
        create_access_tokens(connection)
        connection.close()  # Close the connection after use

if __name__ == "__main__":
    main()
