"""
This module provides functions to connect to a MySQL database, create tables, and fetch client data.

Functions:
- connect(): Connect to the MySQL database.
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

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
            cursorclass=pymysql.cursors.DictCursor
        )
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
