import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from urllib.parse import parse_qs, urlparse

SECRET_KEY = "dev-secret-key"  # or load from environment variable
serializer = URLSafeTimedSerializer(SECRET_KEY)

def parse_qr_data(token_string):
    try:
        # Decrypts payload and enforces max_age of 1 hour (3600 seconds)
        payload = serializer.loads(token_string, salt='qr-payment-salt') # max_age=3600; add later to force age timeout

        order_id = payload['order_id']
        amount = payload['amount']
        user = payload['user']

        return {
            'order_id': order_id,
            'amount': float(amount),
            'user': user
        }
    except SignatureExpired:
        raise ValueError("Payment link has expired!")
    except BadSignature:
        raise ValueError("Invalid or tampered payment link signature!")

def decrypt(url):
    enc_data =parse_qs(urlparse(url).query).get("data", [None])[0]
    dec_data=parse_qr_data(enc_data)
    return dec_data



