import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import Config
from app.database import db_manager

class AuthService:
    @staticmethod
    def register_user(username, email, password, default_city='London'):
        # Check existing username or email
        existing = db_manager.execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
            fetch_one=True
        )
        if existing:
            return {"success": False, "error": "Username or Email already registered"}

        pw_hash = generate_password_hash(password)
        user_id = db_manager.execute_query(
            "INSERT INTO users (username, email, password_hash, default_city) VALUES (?, ?, ?, ?)",
            (username, email, pw_hash, default_city),
            commit=True
        )
        token = AuthService.generate_token(user_id, username)
        return {
            "success": True,
            "user": {"id": user_id, "username": username, "email": email, "default_city": default_city},
            "token": token
        }

    @staticmethod
    def login_user(email_or_username, password):
        user = db_manager.execute_query(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            (email_or_username, email_or_username),
            fetch_one=True
        )
        if not user or not check_password_hash(user["password_hash"], password):
            return {"success": False, "error": "Invalid username/email or password"}

        token = AuthService.generate_token(user["id"], user["username"])
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "default_city": user.get("default_city", "London")
            },
            "token": token
        }

    @staticmethod
    def generate_token(user_id, username):
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return payload
        except Exception:
            return None
