import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response
from decryptor import decrypt
from login import login_required
from bankdb_account_query import query_account_by_accountno, query_account_by_username

app = Flask(__name__)
ACCOUNT_NO = None

@app.route('/')
def index():
    # If cookie is present, redirect to review
    if request.cookies.get("username"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    account = None
    global ACCOUNT_NO

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        account = query_account_by_username(username)

        # Verify credentials against db
        if (account is not None) and username == account[1] and password == account[3]:
            # Create a redirect response and attach the auth cookie
            ACCOUNT_NO = account[0]
            response = make_response(redirect(url_for("dashboard")))

            # httponly prevents JavaScript from stealing the cookie
            response.set_cookie(
                "username", username, httponly=True, samesite="Lax"
            )

            return response
        else:
            error = "Invalid username or password."

        account = None

    return render_template("login.html", error=error)

@app.route('/dashboard', methods=["GET"])
def dashboard():
    # Account data dictionary stored inside the route function
    global ACCOUNT_NO
    account = query_account_by_accountno(ACCOUNT_NO)
    print(account)

    account_info = {
        "customer_name": str(account[2]),
        "account_number": str(account[0]),
        "account_type": str(account[5]),
        "balance": account[4],
    }

    account = None

    return render_template('dashboard.html', account=account_info)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/scan')
def scan_page():
    return render_template('scan.html')

@app.route('/review')
def review_payment():
    full_url = request.url  # for prod
    # full_url = "http://127.0.0.1:5000/pay?data=eyJvcmRlcl9pZCI6IjRBQ0EzNDk1NjAiLCJhbW91bnQiOiIzLjc1IiwidXNlciI6ImFkbWluIn0.amCXng.DcG9403NkV0ctcmgPGF3wslATEI" #request.url

    transaction_data = decrypt(full_url)
    transaction_data["merchant_name"] = "Little Crumbs Patissieries"

    # transaction_data = {
    #     "order_id": "ODR-987654321",
    #     "amount": "₱1,250.00",
    #     "user": "admin"
    #     "merchant_name": "Little Crumbs Patissieries"
    # }
    return render_template('review.html', tx=transaction_data)


@app.route('/process', methods=['POST'])
def process_payment():
    # Here is where you would normally call your payment gateway API.
    # We will simulate a successful transaction for this example.
    # Change this to False to see the failure screen.
    is_successful = True

    return render_template('result.html', success=is_successful)
    
# testing for jenkins webhook1

if __name__ == '__main__':
    # Run on all available IPs so you can test it on your mobile phone
    # by connecting to the same WiFi and visiting your computer's local IP.
    app.run(host='0.0.0.0', port=5001, debug=True)
