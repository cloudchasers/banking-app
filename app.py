import os
import io
import json
import qrcode
import requests
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response, send_file, session
from decryptor import decrypt
from login import login_required
from bankdb_account_query import query_account_by_accountno, query_account_by_username
from bankdb_transaction_query import query_transactions_by_accountno
from pay import proceed_payment
from decryptor import decrypt, parse_qr_data

from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

@app.before_request
def check_banking_session_timeout():
    session.permanent = True
    if request.endpoint == 'static':
        return

    if 'username' in session:
        now = datetime.now(timezone.utc).timestamp()
        last_active = session.get('last_active')
        timeout_seconds = 15 * 60  # 15 minutes session timeout
        
        if last_active and (now - last_active > timeout_seconds):
            session.clear()
            response = make_response(redirect(url_for('login')))
            response.set_cookie("username", "", expires=0)
            return response
            
        session['last_active'] = now

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

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        account = query_account_by_username(username)

        # Verify credentials against db
        if (account is not None) and username == account[1] and password == account[3]:
            session.permanent = True
            session['username'] = username
            session['account_no'] = account[0]
            session['last_active'] = datetime.now(timezone.utc).timestamp()
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)

@app.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    account_no = session.get('account_no')
    account = query_account_by_accountno(account_no)

    account_info = {
        "customer_name": str(account[2]),
        "account_number": str(account[0]),
        "account_type": str(account[5]),
        "balance": account[4],
    }

    return render_template('dashboard.html', account=account_info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/transactions")
@login_required
def transactions():
    account_no = session.get('account_no')
    raw_transactions = query_transactions_by_accountno(account_no)
    processed_transactions = []

    for tx_id, debit_acc, credit_acc, amount in raw_transactions:
        if str(debit_acc) == str(account_no):
            tx_type = "Debit"
            other_party = credit_acc
            formatted_amount = f"-₱{amount:,.2f}"
        else:
            tx_type = "Credit"
            other_party = debit_acc
            formatted_amount = f"+₱{amount:,.2f}"

        processed_transactions.append(
            {
                "id": tx_id,
                "type": tx_type,
                "other_party": other_party,
                "amount": formatted_amount,
            }
        )

    return render_template(
        "transactions.html",
        transactions=processed_transactions,
        account_no=account_no,
    )

@app.route('/scan')
@login_required
def scan_page():
    return render_template('scan.html')

@app.route('/pay')
@app.route('/display_qr')
def display_qr():
    token = request.args.get('data')
    if not token:
        return "<h2>Error: Missing payment data (?data=...)</h2><p>This page should be accessed from the eCommerce checkout.</p>", 400
        
    order_id = None
    try:
        data = parse_qr_data(token)
        order_id = data.get('order_id')
    except Exception as e:
        print(f"QR decode error: {e}")

    return render_template('qr_display.html', token=token, order_id=order_id)


@app.route('/review')
@login_required
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
@login_required
def process_payment():
    # Here is where you would normally call your payment gateway API.
    # We will simulate a successful transaction for this example.
    # Change this to False to see the failure screen.
    is_successful = True
    order_id = request.form.get('order_id')
    pay_amt = request.form.get('amount')
    account_no = session.get('account_no')
    
    if is_successful and order_id and account_no:
        try:
            # update db accounts and transaction
            proceed_payment(account_no, pay_amt)

            # Send webhook to eCommerce app
            ecommerce_base = os.environ.get('ECOMMERCE_PUBLIC_BASE', 'http://127.0.0.1:5000')
            requests.post(f"{ecommerce_base}/api/order/confirm/{order_id}", timeout=5)
        except Exception as e:
            is_successful = False
            print(f"Failed to process or send webhook: {e}")

    return render_template('result.html', success=is_successful)

@app.route('/api/check_status/<order_id>')
def check_status(order_id):
    try:
        ecommerce_base = os.environ.get('ECOMMERCE_PUBLIC_BASE', 'http://127.0.0.1:5000')
        res = requests.get(f"{ecommerce_base}/api/order/status/{order_id}", timeout=5)
        return res.json()
    except Exception as e:
        return {"error": str(e)}, 500
    
# testing for jenkins webhook1

if __name__ == '__main__':
    # Run on all available IPs so you can test it on your mobile phone
    # by connecting to the same WiFi and visiting your computer's local IP.
    app.run(host='0.0.0.0', port=5001, debug=True)
