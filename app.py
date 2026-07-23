import os
import io
import qrcode
import requests
from flask import Flask, render_template, request, send_file
from decryptor import decrypt

app = Flask(__name__)

@app.route('/')
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
            requests.post(f"http://127.0.0.1:5000/api/order/confirm/{order_id}", timeout=5)
        except Exception as e:
            print(f"Failed to send webhook: {e}")

    return render_template('result.html', success=is_successful)


if __name__ == '__main__':
    # Run on all available IPs so you can test it on your mobile phone
    # by connecting to the same WiFi and visiting your computer's local IP.
    app.run(host='0.0.0.0', port=5001, debug=True)
