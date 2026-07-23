import os
import io
import json
import qrcode
import requests
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
from decryptor import decrypt
from login import login_required
from bankdb_account_query import query_account_by_accountno, query_account_by_username

app = Flask(__name__)
ACCOUNT_NO = None

@app.route('/')
def index():
    token = request.args.get('data')
    if token:
        return redirect(url_for('display_qr', data=token))
        
    # If cookie is present, redirect to dashboard
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

@app.route('/display_qr')
def display_qr():
    token = request.args.get('data')
    if not token:
        return "<h2>Error: Missing payment data (?data=...)</h2><p>This page should be accessed from the eCommerce checkout.</p>", 400
    return render_template('qr_display.html', token=token)

@app.route('/review')
def review_payment():
    token = request.args.get('data')

    if not token:
        return "<h2>Error: Missing payment data (?data=...)</h2><p>This page should be accessed from the eCommerce checkout.</p>", 400

    try:
        full_url = request.url  # for prod
        transaction_data = decrypt(full_url)
        transaction_data["merchant_name"] = "Little Crumbs Patissieries"
    except Exception as e:
        return f"<h2>Error: Invalid or expired payment link</h2><p>{e}</p>", 400

    return render_template('review.html', tx=transaction_data, token=token)

@app.route('/qrcode')
def generate_qr():
    token = request.args.get('data')
    if not token:
        return "No token provided", 400
        
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/process', methods=['POST'])
def process_payment():
    # Here is where you would normally call your payment gateway API.
    # We will simulate a successful transaction for this example.
    # Change this to False to see the failure screen.
    is_successful = True
    order_id = request.form.get('order_id')
    
    if is_successful and order_id:
        try:
            # Send webhook to eCommerce app
            ecommerce_base = os.environ.get('ECOMMERCE_PUBLIC_URL', 'http://127.0.0.1:5000')
            requests.post(f"{ecommerce_base}/api/order/confirm/{order_id}", timeout=5)
        except Exception as e:
            print(f"Failed to send webhook: {e}")

    return render_template('result.html', success=is_successful)
    
# testing for jenkins webhook1

if __name__ == '__main__':
    # Run on all available IPs so you can test it on your mobile phone
    # by connecting to the same WiFi and visiting your computer's local IP.
    app.run(host='0.0.0.0', port=5001, debug=True)
