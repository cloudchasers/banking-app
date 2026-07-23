import mysql.connector
from mysql.connector import Error

# Database connection parameters
config = {
    'host': '100.48.217.125',
    'port': 3306,
    'database': 'testsite',
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
        query = "SELECT * FROM transactions"
        cursor.execute(query)

        # 4. Fetch column headers and rows
        column_names = [i[0] for i in cursor.description]
        rows = cursor.fetchall()

        # 5. Display the output
        print("\n--- Transactions Table Contents ---")
        print(" | ".join(column_names))
        print("-" * 50)

        for row in rows:
            print(row)

        print(f"\nTotal rows returned: {len(rows)}")

except Error as e:
    print(f"Error connecting to database: {e}")

finally:
    # 6. Ensure connection and cursor are safely closed
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Database connection closed.")