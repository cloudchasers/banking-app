import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response

# Helper to load users from json file
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}


# Login requirement decorator (Checks cookie instead of session)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Read the 'username' cookie from the incoming request
        if not request.cookies.get("username"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function