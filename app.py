import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def review_payment():
    # Static values for now — eventually, you'll pull these from a database
    # using an ID passed in the QR code URL.
    transaction_data = {
        "merchant_name": "Main Application Store",
        "amount": "₱1,250.00",
        "order_id": "ODR-987654321"
    }
    return render_template('review.html', tx=transaction_data)


@app.route('/process', methods=['POST'])
def process_payment():
    # Here is where you would normally call your payment gateway API.
    # We will simulate a successful transaction for this example.
    # Change this to False to see the failure screen.
    is_successful = True

    return render_template('result.html', success=is_successful)


if __name__ == '__main__':
    # Run on all available IPs so you can test it on your mobile phone
    # by connecting to the same WiFi and visiting your computer's local IP.
    app.run(host='0.0.0.0', port=5000, debug=True)