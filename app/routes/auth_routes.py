from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.database import db_manager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    default_city = data.get('default_city', 'London').strip()

    if not username or not email or not password:
        return jsonify({"success": False, "error": "Username, email, and password are required"}), 400

    result = AuthService.register_user(username, email, password, default_city)
    if not result.get("success"):
        return jsonify(result), 400
    return jsonify(result)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    login_id = data.get('username_or_email', '').strip()
    password = data.get('password', '')

    if not login_id or not password:
        return jsonify({"success": False, "error": "Username/email and password are required"}), 400

    result = AuthService.login_user(login_id, password)
    if not result.get("success"):
        return jsonify(result), 401
    return jsonify(result)

@auth_bp.route('/api/auth/me', methods=['GET'])
def get_me():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    payload = AuthService.verify_token(token)
    if not payload:
        return jsonify({"success": False, "error": "Invalid or expired token"}), 401

    user_id = payload.get('user_id')
    user = db_manager.execute_query(
        "SELECT id, username, email, default_city, created_at FROM users WHERE id = ?",
        (user_id,),
        fetch_one=True
    )
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    return jsonify({"success": True, "user": user})
