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

try:
    # 1. Establish the connection
    print("Connecting to MySQL database...")
    connection = mysql.connector.connect(**config)

    if connection.is_connected():
        # 2. Create a cursor object
        cursor = connection.cursor()

        # 3. Execute query to select all data from the table
        query = "SELECT * FROM accounts"
        cursor.execute(query)

        # 4. Fetch column headers and rows
        column_names = [i[0] for i in cursor.description]
        rows = cursor.fetchall()

        print(rows)
        print(type(rows))


except Error as e:
    print(f"Error connecting to database: {e}")

finally:
    # 6. Ensure connection and cursor are safely closed
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Database connection closed.")