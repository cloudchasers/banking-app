import mysql.connector
from mysql.connector import Error

# Database connection parameters
config = {
    'host': '54.157.54.209',
    'port': 3306,
    'database': 'bankingdb',
    'user': 'webuser',
    'password': 'MyStrongPassword123!'
}

def query_transactions_by_accountno(accountno):
    try:
        # 1. Establish the connection
        print("Connecting to MySQL database...")
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            # 2. Create a cursor object
            cursor = connection.cursor()

            # 3. Execute query to select all data from the table
            query = f"SELECT * FROM transactions WHERE debit_account = '{accountno}' OR credit_account = '{accountno}'"
            cursor.execute(query)

            history = cursor.fetchall()
            print(history)

    except Error as e:
        print(f"Error connecting to database: {e}")

    finally:
        # 6. Ensure connection and cursor are safely closed
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Database connection closed.")

    return history