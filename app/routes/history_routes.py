from flask import Blueprint, request, jsonify
from app.services.openmeteo_service import OpenMeteoService
from app.database import db_manager

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['GET'])
def get_history():
    try:
        lat = float(request.args.get('lat', 51.5074))
        lon = float(request.args.get('lon', -0.1278))
        days = int(request.args.get('days', 7))
        units = request.args.get('units', 'c')
        city_name = request.args.get('city', '')

        # Fetch historical weather analytics from Open-Meteo
        analytics = OpenMeteoService.fetch_history_analytics(lat, lon, days, units)
        
        # Also query logged database history for city if available
        logged_weather = []
        if city_name:
            logged_weather = db_manager.execute_query(
                "SELECT * FROM weather_history WHERE city_name = ? ORDER BY created_at DESC LIMIT 20",
                (city_name,),
                fetch_all=True
            ) or []

        return jsonify({
            "success": True,
            "analytics": analytics,
            "logged_history": logged_weather
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
