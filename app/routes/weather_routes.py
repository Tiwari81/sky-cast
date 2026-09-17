from flask import Blueprint, request, jsonify
from app.services.openmeteo_service import OpenMeteoService
from app.services.weather_provider import WeatherProvider
from app.services.alerts_service import AlertsService
from app.database import db_manager

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        lat = float(request.args.get('lat', 51.5074))
        lon = float(request.args.get('lon', -0.1278))
        units = request.args.get('units', 'c')
        city_name = request.args.get('city', 'Selected Location')

        data = WeatherProvider.get_current_weather(lat, lon, units)
        data['city_name'] = city_name
        
        # Log to weather_history table
        try:
            db_manager.execute_query(
                """INSERT INTO weather_history 
                   (city_name, latitude, longitude, temp_c, condition_text, humidity, wind_kph, uv_index) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (city_name, lat, lon, data['temperature'], data['condition'], data['humidity'], 
                 data['wind']['speed'], data['uv_index']),
                commit=True
            )
        except Exception as log_err:
            pass

        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@weather_bp.route('/api/forecast', methods=['GET'])
def get_forecast():
    try:
        lat = float(request.args.get('lat', 51.5074))
        lon = float(request.args.get('lon', -0.1278))
        units = request.args.get('units', 'c')

        data = OpenMeteoService.fetch_forecast(lat, lon, units)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@weather_bp.route('/api/aqi', methods=['GET'])
def get_aqi():
    try:
        lat = float(request.args.get('lat', 51.5074))
        lon = float(request.args.get('lon', -0.1278))
        city_name = request.args.get('city', 'Selected Location')

        data = OpenMeteoService.fetch_air_quality(lat, lon)
        
        # Log to aqi_history table
        try:
            p = data['pollutants']
            db_manager.execute_query(
                """INSERT INTO aqi_history 
                   (city_name, latitude, longitude, aqi_value, aqi_category, pm25, pm10, co, no2, so2, o3) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (city_name, lat, lon, data['aqi'], data['category'], 
                 p['pm2_5'], p['pm10'], p['co'], p['no2'], p['so2'], p['o3']),
                commit=True
            )
        except Exception:
            pass

        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@weather_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        lat = float(request.args.get('lat', 51.5074))
        lon = float(request.args.get('lon', -0.1278))
        units = request.args.get('units', 'c')

        weather_data = OpenMeteoService.fetch_current_weather(lat, lon, units)
        aqi_data = OpenMeteoService.fetch_air_quality(lat, lon)
        
        alerts = AlertsService.generate_alerts(weather_data, aqi_data)
        return jsonify({"success": True, "alerts": alerts})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
