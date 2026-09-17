from flask import Blueprint, request, jsonify
from app.services.openmeteo_service import OpenMeteoService

location_bp = Blueprint('location', __name__)

@location_bp.route('/api/location/search', methods=['GET'])
def search_location():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"success": True, "results": []})
    
    try:
        results = OpenMeteoService.search_location(query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@location_bp.route('/api/location/reverse', methods=['GET'])
def reverse_geocode():
    try:
        lat = float(request.args.get('lat', 51.5074))
        lon = float(request.args.get('lon', -0.1278))
        res = OpenMeteoService.reverse_geocode(lat, lon)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
