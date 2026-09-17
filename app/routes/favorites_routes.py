from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.database import db_manager

favorites_bp = Blueprint('favorites', __name__)

def get_current_user_id(req):
    auth_header = req.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        payload = AuthService.verify_token(token)
        if payload:
            return payload.get('user_id')
    return None

@favorites_bp.route('/api/favorites', methods=['GET'])
def get_favorites():
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({"success": True, "favorites": [], "guest": True})
    
    try:
        favs = db_manager.execute_query(
            "SELECT id, city_name, country, latitude, longitude, created_at FROM favorite_locations WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
            fetch_all=True
        ) or []
        return jsonify({"success": True, "favorites": favs, "guest": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@favorites_bp.route('/api/favorites', methods=['POST'])
def add_favorite():
    user_id = get_current_user_id(request)
    data = request.json or {}
    city_name = data.get('city_name')
    country = data.get('country', '')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not city_name or latitude is None or longitude is None:
        return jsonify({"success": False, "error": "City name, latitude, and longitude are required"}), 400

    if not user_id:
        # Return success for guest mode so frontend can cache in localStorage
        return jsonify({"success": True, "guest": True, "message": "Saved to guest local storage"})

    try:
        # Check if already added
        existing = db_manager.execute_query(
            "SELECT id FROM favorite_locations WHERE user_id = ? AND city_name = ?",
            (user_id, city_name),
            fetch_one=True
        )
        if existing:
            return jsonify({"success": True, "message": "City already in favorites"})

        fav_id = db_manager.execute_query(
            "INSERT INTO favorite_locations (user_id, city_name, country, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
            (user_id, city_name, country, latitude, longitude),
            commit=True
        )
        return jsonify({"success": True, "id": fav_id, "message": "Added to favorites"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@favorites_bp.route('/api/favorites/<city_name>', methods=['DELETE'])
def remove_favorite(city_name):
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({"success": True, "guest": True, "message": "Removed from guest local storage"})

    try:
        db_manager.execute_query(
            "DELETE FROM favorite_locations WHERE user_id = ? AND city_name = ?",
            (user_id, city_name),
            commit=True
        )
        return jsonify({"success": True, "message": "Removed from favorites"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
