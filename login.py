import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response

# # Helper to load users from json file
# def load_users():
#     if os.path.exists('users.json'):
#         with open('users.json', 'r') as f:
#             return json.load(f)
#     return {}


from flask import redirect, url_for, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged into the session
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function