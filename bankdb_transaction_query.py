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

def process_transaction(username, amount):
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 1. Fetch current balance
            cursor.execute(f"SELECT balance FROM accounts WHERE username = '{username}'")
            result = cursor.fetchone()
            
            if not result:
                return False
                
            current_balance = float(result[0])
            amount = float(amount)
            
            # 2. Check if sufficient balance
            if current_balance < amount:
                return False
                
            # 3. Deduct balance
            new_balance = current_balance - amount
            cursor.execute(f"UPDATE accounts SET balance = {new_balance} WHERE username = '{username}'")
            
            connection.commit()
            return True
            
    except Error as e:
        print(f"Error processing transaction: {e}")
        return False
        
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
