"""
This module implements a Flask application for client authentication.
It includes database connection.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'model')))

from model.main import main, get_connection
from model.connect import connect_to_mysql_db
from model.create_client_table import create_client_table
from model.create_access_tokens import create_access_tokens

# Example usage of get_connection():
connection = get_connection()

if connection:

    create_client_table(connection)
    create_access_tokens(connection)
    # # Perform operations using the database connection
    # cursor = connection.cursor()
    # cursor.execute("SELECT * FROM client")
    # rows = cursor.fetchall()
    # for row in rows:
    #     # print(row)
    #     pass
    # connection.close()
else:
    print("No database connection available.")

if __name__ == "__main__":
    main()
