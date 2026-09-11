import jwt
from functools import wraps
from flask import request, redirect, url_for

JWT_SECRET = "support_pilot_secure_jwt_key_2026"
JWT_ALGORITHM = "HS256"

def generate_token(full_name, email):
    """Generates a signed JWT token containing user metadata."""
    payload = {
        "full_name": full_name,
        "email": email
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def token_required(f):
    """Decorator to protect routes requiring authentication via JWT cookies."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("auth_token")
        if not token:
            return redirect(url_for("login"))
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_email = data["email"]
            request.user_name = data["full_name"]
        except Exception:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated