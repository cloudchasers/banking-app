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

def proceed_payment(debit_account, amount):
    credit_account = "100000000001"

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # 1. UPDATE Query using f-strings
        # Note: Numeric values don't need quotes, but string account numbers do ('{account_no}')
        update_debit = f"UPDATE accounts SET balance = balance - {amount} WHERE account_no = '{debit_account}'"
        update_credit = f"UPDATE accounts SET balance = balance + {amount} WHERE account_no = '{credit_account}'"

        # Execute updates
        cursor.execute(update_debit)
        cursor.execute(update_credit)

        # 2. INSERT Query using f-strings
        insert_transaction = f"INSERT INTO transactions (debit_account, credit_account, amount) VALUES ('{debit_account}', '{credit_account}', {amount})"

        # Execute insert
        cursor.execute(insert_transaction)

        # Save all changes permanently
        connection.commit()

        print("Payment and transaction successfully recorded!")

    except Error as err:
        print(f"Error: {err}")
        connection.rollback()

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

