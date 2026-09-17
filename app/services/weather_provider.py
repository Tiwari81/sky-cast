import os
import requests
from app.config import Config
from app.services.openmeteo_service import OpenMeteoService

class WeatherProvider:
    @staticmethod
    def get_current_weather(lat, lon, units="c"):
        owm_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
        wapi_key = os.getenv("WEATHERAPI_KEY", "").strip()

        # 1. Try OpenWeatherMap if key provided
        if owm_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owm_key}&units=metric"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    d = resp.json()
                    temp_c = d["main"]["temp"]
                    feels_c = d["main"]["feels_like"]
                    is_imperial = (units.lower() == 'f')
                    
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "temperature": round((temp_c * 9/5) + 32, 1) if is_imperial else temp_c,
                        "feels_like": round((feels_c * 9/5) + 32, 1) if is_imperial else feels_c,
                        "temp_unit": "°F" if is_imperial else "°C",
                        "condition": d["weather"][0]["main"],
                        "icon": d["weather"][0]["icon"],
                        "weather_code": d["weather"][0]["id"],
                        "humidity": d["main"]["humidity"],
                        "pressure_hpa": d["main"]["pressure"],
                        "visibility_km": round(d.get("visibility", 10000) / 1000, 1),
                        "cloud_cover": d.get("clouds", {}).get("all", 0),
                        "dew_point": round(temp_c - ((100 - d["main"]["humidity"]) / 5), 1),
                        "uv_index": 5.0,
                        "is_day": 1,
                        "wind": {
                            "speed": round(d["wind"]["speed"] * 3.6 * 0.621371, 1) if is_imperial else round(d["wind"]["speed"] * 3.6, 1),
                            "speed_unit": "mph" if is_imperial else "km/h",
                            "direction": d["wind"].get("deg", 0),
                            "gust": round(d["wind"].get("gust", d["wind"]["speed"]) * 3.6, 1)
                        },
                        "sun": {
                            "sunrise": str(d.get("sys", {}).get("sunrise", "")),
                            "sunset": str(d.get("sys", {}).get("sunset", ""))
                        },
                        "moon": {"phase_name": "Waxing Gibbous", "illumination": 75}
                    }
            except Exception as e:
                print(f"OpenWeatherMap API error ({e}), falling back to Open-Meteo...")

        # 2. Try WeatherAPI if key provided
        if wapi_key:
            try:
                url = f"http://api.weatherapi.com/v1/current.json?key={wapi_key}&q={lat},{lon}"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    d = resp.json().get("current", {})
                    is_imperial = (units.lower() == 'f')
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "temperature": d.get("temp_f") if is_imperial else d.get("temp_c"),
                        "feels_like": d.get("feelslike_f") if is_imperial else d.get("feelslike_c"),
                        "temp_unit": "°F" if is_imperial else "°C",
                        "condition": d.get("condition", {}).get("text", "Clear"),
                        "icon": "01d",
                        "weather_code": 0,
                        "humidity": d.get("humidity", 0),
                        "pressure_hpa": d.get("pressure_mb", 1013),
                        "visibility_km": d.get("vis_km", 10),
                        "cloud_cover": d.get("cloud", 0),
                        "dew_point": d.get("dewpoint_c", 0),
                        "uv_index": d.get("uv", 0),
                        "is_day": d.get("is_day", 1),
                        "wind": {
                            "speed": d.get("wind_mph") if is_imperial else d.get("wind_kph"),
                            "speed_unit": "mph" if is_imperial else "km/h",
                            "direction": d.get("wind_degree", 0),
                            "gust": d.get("gust_mph") if is_imperial else d.get("gust_kph")
                        },
                        "sun": {"sunrise": "--", "sunset": "--"},
                        "moon": {"phase_name": "Waxing Gibbous", "illumination": 75}
                    }
            except Exception as e:
                print(f"WeatherAPI error ({e}), falling back to Open-Meteo...")

        # 3. Default: Open-Meteo (Requires NO API key at all!)
        return OpenMeteoService.fetch_current_weather(lat, lon, units)
