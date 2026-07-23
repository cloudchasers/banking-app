import os
from flask import Flask, render_template, request
from decryptor import decrypt

app = Flask(__name__)
full_url = request.url #for prod
# full_url = "http://127.0.0.1:5000/pay?data=eyJvcmRlcl9pZCI6IjRBQ0EzNDk1NjAiLCJhbW91bnQiOiIzLjc1IiwidXNlciI6ImFkbWluIn0.amCXng.DcG9403NkV0ctcmgPGF3wslATEI" #request.url

@app.route('/')
def review_payment():

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


if __name__ == '__main__':
    # Run on all available IPs so you can test it on your mobile phone
    # by connecting to the same WiFi and visiting your computer's local IP.
    app.run(host='0.0.0.0', port=5001, debug=True)