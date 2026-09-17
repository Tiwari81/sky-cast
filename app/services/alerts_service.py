class AlertsService:
    @staticmethod
    def generate_alerts(weather_data, aqi_data=None):
        alerts = []
        
        temp = weather_data.get("temperature", 0)
        temp_unit = weather_data.get("temp_unit", "°C")
        temp_c = temp if temp_unit == "°C" else (temp - 32) * 5/9
        
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        wind_unit = weather_data.get("wind", {}).get("speed_unit", "km/h")
        wind_kph = wind_speed if wind_unit == "km/h" else wind_speed * 1.60934
        
        weather_code = weather_data.get("weather_code", 0)
        
        # 1. Extreme Temperature Alerts
        if temp_c >= 35.0:
            alerts.append({
                "id": "alert-heat",
                "type": "Extreme Temperature",
                "severity": "High",
                "badge_class": "badge-danger",
                "title": "Extreme Heat Advisory",
                "message": f"Temperature is currently {temp}{temp_unit}. Stay hydrated, avoid direct sun exposure during peak hours, and check on vulnerable individuals.",
                "icon": "fa-fire-flame-curved"
            })
        elif temp_c <= 0.0:
            alerts.append({
                "id": "alert-freeze",
                "type": "Extreme Temperature",
                "severity": "Warning",
                "badge_class": "badge-warning",
                "title": "Freezing Temperature Warning",
                "message": f"Freezing conditions detected at {temp}{temp_unit}. Watch out for icy road conditions and protect outdoor pipes and pets.",
                "icon": "fa-snowflake"
            })

        # 2. Heavy Rain / Thunderstorm Alert
        if weather_code in [65, 82, 95, 96, 99]:
            alerts.append({
                "id": "alert-heavy-rain",
                "type": "Severe Weather",
                "severity": "High",
                "badge_class": "badge-danger",
                "title": "Heavy Precipitation / Thunderstorm Warning",
                "message": "Torrential rain or severe thunderstorm activity is ongoing. Exercise extreme caution while driving and stay indoors.",
                "icon": "fa-cloud-showers-heavy"
            })
        elif weather_code in [61, 63, 80, 81]:
            alerts.append({
                "id": "alert-rain",
                "type": "Rain Advisory",
                "severity": "Info",
                "badge_class": "badge-info",
                "title": "Active Rainfall",
                "message": "Light to moderate rain detected in your area. Carry an umbrella when going outdoors.",
                "icon": "fa-cloud-rain"
            })

        # 3. High Wind Alert
        if wind_kph >= 45.0:
            alerts.append({
                "id": "alert-wind-high",
                "type": "High Wind",
                "severity": "High",
                "badge_class": "badge-danger",
                "title": "Gale Wind Warning",
                "message": f"High wind speeds of {wind_speed} {wind_unit} recorded. Secure outdoor items and beware of falling tree branches.",
                "icon": "fa-wind"
            })
        elif wind_kph >= 30.0:
            alerts.append({
                "id": "alert-wind-mod",
                "type": "Breezy Wind",
                "severity": "Info",
                "badge_class": "badge-info",
                "title": "Breezy Conditions",
                "message": f"Breezy winds up to {wind_speed} {wind_unit}.",
                "icon": "fa-wind"
            })

        # 4. Air Quality Alert
        if aqi_data:
            aqi = aqi_data.get("aqi", 0)
            category = aqi_data.get("category", "Good")
            if aqi > 150:
                alerts.append({
                    "id": "alert-aqi-unhealthy",
                    "type": "Air Quality Alert",
                    "severity": "Severe",
                    "badge_class": "badge-danger",
                    "title": f"Unhealthy Air Quality (AQI {aqi} - {category})",
                    "message": "Air pollution is elevated. Sensitive groups and outdoor enthusiasts should restrict strenuous outdoor activities and wear an N95 mask.",
                    "icon": "fa-smog"
                })
            elif aqi > 100:
                alerts.append({
                    "id": "alert-aqi-mod",
                    "type": "Air Quality Advisory",
                    "severity": "Warning",
                    "badge_class": "badge-warning",
                    "title": f"Moderate Air Quality (AQI {aqi} - {category})",
                    "message": "Sensitive individuals may experience respiratory discomfort during outdoor exposure.",
                    "icon": "fa-smog"
                })

        return alerts
