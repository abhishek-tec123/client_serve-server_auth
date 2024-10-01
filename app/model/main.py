"""
This module provides functions to connect to a MySQL database, create tables, and fetch client data.

Functions:
- connect(): Connect to the MySQL database.
"""

# from connect import connect_to_mysql_db
# from create_client_table import create_client_table
# from create_access_tokens import create_access_tokens
# from fetch_client_data import fetch_client_data

# def main():
#     """
#     Main function to create tables and fetch client data.
#     """
#     connection = connect_to_mysql_db()
#     if connection:
#         create_client_table(connection)
#         create_access_tokens(connection)

#         # Example: Fetch client data by name
#         client_name = 'abhishek'
#         client_data = fetch_client_data(client_name)
#         if client_data:
#             print(f"Client data for '{client_name}':")
#             for row in client_data:
#                 print(row)
#         connection.close()

# if __name__ == "__main__":
#     main()


from model.connect import connect_to_mysql_db
from model.create_client_table import create_client_table
from model.create_access_tokens import create_access_tokens
# from fetch_client_data import fetch_client_data

# Establish connection
conn = connect_to_mysql_db()

def main():
    """
    Main function to create tables and fetch client data.
    """

    if conn:
        create_client_table(conn)
        create_access_tokens(conn)

        # Example: Fetch client data by name
        # client_name = 'abhishek'
        # client_data = fetch_client_data(conn, client_name)
        # if client_data:
        #     print(f"Client data for '{client_name}':")
        #     for row in client_data:
        #         print(row)
        # conn.close()

def get_connection():
    """
    Returns the database connection object.
    """
    return conn

if __name__ == "__main__":
    main()
