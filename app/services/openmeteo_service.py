import requests
import math
from datetime import datetime
from app.config import Config

WMO_CODE_MAP = {
    0: {"condition": "Clear Sky", "icon": "clear-day"},
    1: {"condition": "Mainly Clear", "icon": "partly-cloudy-day"},
    2: {"condition": "Partly Cloudy", "icon": "partly-cloudy-day"},
    3: {"condition": "Overcast", "icon": "cloudy"},
    45: {"condition": "Foggy", "icon": "fog"},
    48: {"condition": "Depositing Rime Fog", "icon": "fog"},
    51: {"condition": "Light Drizzle", "icon": "drizzle"},
    53: {"condition": "Moderate Drizzle", "icon": "drizzle"},
    55: {"condition": "Dense Drizzle", "icon": "drizzle"},
    56: {"condition": "Freezing Drizzle", "icon": "rain-snow"},
    57: {"condition": "Dense Freezing Drizzle", "icon": "rain-snow"},
    61: {"condition": "Slight Rain", "icon": "rain"},
    63: {"condition": "Moderate Rain", "icon": "rain"},
    65: {"condition": "Heavy Rain", "icon": "heavy-rain"},
    66: {"condition": "Light Freezing Rain", "icon": "rain-snow"},
    67: {"condition": "Heavy Freezing Rain", "icon": "rain-snow"},
    71: {"condition": "Slight Snow", "icon": "snow"},
    73: {"condition": "Moderate Snow", "icon": "snow"},
    75: {"condition": "Heavy Snow", "icon": "heavy-snow"},
    77: {"condition": "Snow Grains", "icon": "snow"},
    80: {"condition": "Slight Rain Showers", "icon": "rain"},
    81: {"condition": "Moderate Rain Showers", "icon": "rain"},
    82: {"condition": "Violent Rain Showers", "icon": "heavy-rain"},
    85: {"condition": "Slight Snow Showers", "icon": "snow"},
    86: {"condition": "Heavy Snow Showers", "icon": "heavy-snow"},
    95: {"condition": "Thunderstorm", "icon": "thunderstorm"},
    96: {"condition": "Thunderstorm & Hail", "icon": "thunderstorm"},
    99: {"condition": "Heavy Thunderstorm", "icon": "thunderstorm"}
}

def get_wmo_info(code):
    return WMO_CODE_MAP.get(code, {"condition": "Unknown Weather", "icon": "partly-cloudy-day"})

def calculate_dew_point(temp_c, humidity):
    """Accurate Magnus-Tetens formula for Dew Point"""
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)

def get_moon_phase(dt=None):
    """Calculates approximate moon phase and illumination percentage"""
    if dt is None:
        dt = datetime.now()
    year = dt.year
    month = dt.month
    day = dt.day
    if month < 3:
        year -= 1
        month += 12
    month += 1
    c = 365.25 * year
    e = 30.6 * month
    jd = c + e + day - 694039.09  # Julian date relative to Jan 1900
    jd /= 29.5305882  # Divide by synodic month (29.53 days)
    b = int(jd)
    jd -= b  # Fractional part of cycle (0.0 to 1.0)
    phase_val = round(jd * 8)
    if phase_val >= 8:
        phase_val = 0
    
    phases = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"
    ]
    illumination = round((1 - math.cos(jd * 2 * math.pi)) / 2 * 100)
    return {
        "phase_name": phases[phase_val],
        "illumination": illumination,
        "phase_val": phase_val
    }

class OpenMeteoService:
    @staticmethod
    def fetch_current_weather(lat, lon, units="c"):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "is_day", "precipitation", "rain", "showers", "weather_code",
                "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m",
                "wind_direction_10m", "wind_gusts_10m"
            ],
            "daily": ["sunrise", "sunset", "uv_index_max"],
            "timezone": "auto"
        }
        
        resp = requests.get(Config.OPEN_METEO_WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp_c = current.get("temperature_2m", 0.0)
        feels_c = current.get("apparent_temperature", temp_c)
        humidity = current.get("relative_humidity_2m", 0)
        wind_kph = current.get("wind_speed_10m", 0.0)
        gust_kph = current.get("wind_gusts_10m", wind_kph)
        pressure = current.get("pressure_msl", current.get("surface_pressure", 1013))
        cloud_cover = current.get("cloud_cover", 0)
        weather_code = current.get("weather_code", 0)
        is_day = current.get("is_day", 1)
        wmo = get_wmo_info(weather_code)
        
        dew_point_c = calculate_dew_point(temp_c, humidity)
        
        sunrise = daily.get("sunrise", ["--T--"])[0]
        sunset = daily.get("sunset", ["--T--"])[0]
        uv_max = daily.get("uv_index_max", [0.0])[0]
        
        # Estimate visibility from cloud cover & humidity if not explicitly in current
        visibility_km = max(1.0, round(20.0 * (1 - (humidity / 200.0) - (cloud_cover / 300.0)), 1))
        
        # Unit Conversions if unit system requested is 'f' (Imperial)
        is_imperial = (units.lower() == 'f')
        temp_disp = round((temp_c * 9/5) + 32, 1) if is_imperial else temp_c
        feels_disp = round((feels_c * 9/5) + 32, 1) if is_imperial else feels_c
        dew_disp = round((dew_point_c * 9/5) + 32, 1) if is_imperial else dew_point_c
        wind_disp = round(wind_kph * 0.621371, 1) if is_imperial else wind_kph
        gust_disp = round(gust_kph * 0.621371, 1) if is_imperial else gust_kph
        
        moon_info = get_moon_phase()

        return {
            "latitude": lat,
            "longitude": lon,
            "temperature": temp_disp,
            "feels_like": feels_disp,
            "temp_unit": "°F" if is_imperial else "°C",
            "condition": wmo["condition"],
            "icon": wmo["icon"],
            "weather_code": weather_code,
            "humidity": humidity,
            "pressure_hpa": pressure,
            "visibility_km": visibility_km,
            "cloud_cover": cloud_cover,
            "dew_point": dew_disp,
            "uv_index": uv_max,
            "is_day": is_day,
            "wind": {
                "speed": wind_disp,
                "speed_unit": "mph" if is_imperial else "km/h",
                "direction": current.get("wind_direction_10m", 0),
                "gust": gust_disp
            },
            "sun": {
                "sunrise": sunrise,
                "sunset": sunset
            },
            "moon": moon_info
        }

    @staticmethod
    def fetch_forecast(lat, lon, units="c"):
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": [
                "temperature_2m", "relative_humidity_2m", "precipitation_probability",
                "rain", "weather_code", "pressure_msl", "wind_speed_10m", "uv_index"
            ],
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "apparent_temperature_max", "apparent_temperature_min",
                "sunrise", "sunset", "uv_index_max", "precipitation_sum",
                "precipitation_probability_max", "wind_speed_10m_max"
            ],
            "timezone": "auto"
        }
        
        resp = requests.get(Config.OPEN_METEO_WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        is_imperial = (units.lower() == 'f')
        hourly_raw = data.get("hourly", {})
        daily_raw = data.get("daily", {})
        
        # Build 24-Hour Forecast array
        hourly_list = []
        times = hourly_raw.get("time", [])[:24]
        temps = hourly_raw.get("temperature_2m", [])[:24]
        hums = hourly_raw.get("relative_humidity_2m", [])[:24]
        pop = hourly_raw.get("precipitation_probability", [])[:24]
        codes = hourly_raw.get("weather_code", [])[:24]
        winds = hourly_raw.get("wind_speed_10m", [])[:24]
        uvs = hourly_raw.get("uv_index", [])[:24]
        
        for i in range(len(times)):
            t_val = temps[i] if i < len(temps) else 0.0
            w_val = winds[i] if i < len(winds) else 0.0
            if is_imperial:
                t_val = round((t_val * 9/5) + 32, 1)
                w_val = round(w_val * 0.621371, 1)
                
            code = codes[i] if i < len(codes) else 0
            wmo = get_wmo_info(code)
            hourly_list.append({
                "time": times[i],
                "temp": t_val,
                "humidity": hums[i] if i < len(hums) else 0,
                "rain_prob": pop[i] if i < len(pop) else 0,
                "weather_code": code,
                "condition": wmo["condition"],
                "icon": wmo["icon"],
                "wind_speed": w_val,
                "uv_index": uvs[i] if i < len(uvs) else 0.0
            })
            
        # Build 7-Day Forecast array
        daily_list = []
        d_times = daily_raw.get("time", [])[:7]
        d_maxs = daily_raw.get("temperature_2m_max", [])[:7]
        d_mins = daily_raw.get("temperature_2m_min", [])[:7]
        d_codes = daily_raw.get("weather_code", [])[:7]
        d_pops = daily_raw.get("precipitation_probability_max", [])[:7]
        d_precips = daily_raw.get("precipitation_sum", [])[:7]
        d_winds = daily_raw.get("wind_speed_10m_max", [])[:7]
        d_uvs = daily_raw.get("uv_index_max", [])[:7]
        d_sunrises = daily_raw.get("sunrise", [])[:7]
        d_sunsets = daily_raw.get("sunset", [])[:7]
        
        for i in range(len(d_times)):
            t_max = d_maxs[i] if i < len(d_maxs) else 0.0
            t_min = d_mins[i] if i < len(d_mins) else 0.0
            w_max = d_winds[i] if i < len(d_winds) else 0.0
            if is_imperial:
                t_max = round((t_max * 9/5) + 32, 1)
                t_min = round((t_min * 9/5) + 32, 1)
                w_max = round(w_max * 0.621371, 1)
            code = d_codes[i] if i < len(d_codes) else 0
            wmo = get_wmo_info(code)
            
            daily_list.append({
                "date": d_times[i],
                "temp_max": t_max,
                "temp_min": t_min,
                "condition": wmo["condition"],
                "icon": wmo["icon"],
                "weather_code": code,
                "rain_prob": d_pops[i] if i < len(d_pops) else 0,
                "rain_sum_mm": d_precips[i] if i < len(d_precips) else 0.0,
                "wind_max": w_max,
                "uv_max": d_uvs[i] if i < len(d_uvs) else 0.0,
                "sunrise": d_sunrises[i] if i < len(d_sunrises) else "",
                "sunset": d_sunsets[i] if i < len(d_sunsets) else ""
            })

        return {
            "hourly": hourly_list,
            "daily": daily_list,
            "unit": "°F" if is_imperial else "°C"
        }

    @staticmethod
    def fetch_air_quality(lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "us_aqi", "european_aqi", "pm10", "pm2_5",
                "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone"
            ],
            "timezone": "auto"
        }
        
        resp = requests.get(Config.OPEN_METEO_AIR_QUALITY_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current", {})
        
        us_aqi = current.get("us_aqi", 0)
        
        # Determine AQI category & status badge color
        if us_aqi <= 50:
            category = "Good"
            color = "#10B981"
            health_desc = "Air quality is satisfactory, and air pollution poses little or no risk."
        elif us_aqi <= 100:
            category = "Moderate"
            color = "#F59E0B"
            health_desc = "Air quality is acceptable; however, sensitive individuals may experience minor symptoms."
        elif us_aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
            color = "#F97316"
            health_desc = "Members of sensitive groups may experience health effects. General public is less likely to be affected."
        elif us_aqi <= 200:
            category = "Unhealthy"
            color = "#EF4444"
            health_desc = "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects."
        elif us_aqi <= 300:
            category = "Very Unhealthy"
            color = "#8B5CF6"
            health_desc = "Health alert: The risk of health effects is increased for everyone."
        else:
            category = "Hazardous"
            color = "#7F1D1D"
            health_desc = "Health warning of emergency conditions: The entire population is likely to be affected."

        return {
            "aqi": us_aqi,
            "category": category,
            "color": color,
            "health_recommendation": health_desc,
            "pollutants": {
                "pm2_5": round(current.get("pm2_5", 0.0), 1),
                "pm10": round(current.get("pm10", 0.0), 1),
                "co": round(current.get("carbon_monoxide", 0.0), 1),
                "no2": round(current.get("nitrogen_dioxide", 0.0), 1),
                "so2": round(current.get("sulphur_dioxide", 0.0), 1),
                "o3": round(current.get("ozone", 0.0), 1)
            }
        }

    @staticmethod
    def search_location(query):
        params = {
            "name": query,
            "count": 10,
            "language": "en",
            "format": "json"
        }
        resp = requests.get(Config.OPEN_METEO_GEOCODING_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        
        locations = []
        for r in results:
            locations.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "country": r.get("country", ""),
                "admin1": r.get("admin1", ""),
                "latitude": r.get("latitude"),
                "longitude": r.get("longitude"),
                "timezone": r.get("timezone", "UTC"),
                "population": r.get("population", 0)
            })
        return locations

    @staticmethod
    def reverse_geocode(lat, lon):
        headers = {'User-Agent': 'SkyCastWeatherApp/1.0'}
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }
        try:
            resp = requests.get(Config.OPEN_METEO_REVERSE_GEO_URL, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get('address', {})
                city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('county') or 'Location'
                country = addr.get('country', '')
                return {"city": city, "country": country, "latitude": lat, "longitude": lon}
        except Exception:
            pass
        return {"city": "Current Location", "country": "", "latitude": lat, "longitude": lon}

    @staticmethod
    def fetch_history_analytics(lat, lon, days=7, units="c"):
        """Fetches historical analytics for charts: Temp, Humidity, AQI, Wind, Rain"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "past_days": days,
            "hourly": [
                "temperature_2m", "relative_humidity_2m", "rain",
                "wind_speed_10m"
            ],
            "timezone": "auto"
        }
        resp = requests.get(Config.OPEN_METEO_WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Air quality history
        aqi_params = {
            "latitude": lat,
            "longitude": lon,
            "past_days": days,
            "hourly": ["us_aqi"],
            "timezone": "auto"
        }
        aqi_data = {}
        try:
            aqi_resp = requests.get(Config.OPEN_METEO_AIR_QUALITY_URL, params=aqi_params, timeout=5)
            if aqi_resp.status_code == 200:
                aqi_data = aqi_resp.json().get("hourly", {})
        except Exception:
            pass

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        hums = hourly.get("relative_humidity_2m", [])
        rains = hourly.get("rain", [])
        winds = hourly.get("wind_speed_10m", [])
        aqis = aqi_data.get("us_aqi", [])

        is_imperial = (units.lower() == 'f')
        formatted_temps = [round((t * 9/5) + 32, 1) if is_imperial else t for t in temps]
        formatted_winds = [round(w * 0.621371, 1) if is_imperial else w for w in winds]

        # Sample every 3 hours for clean interactive charts
        step = 3
        return {
            "labels": [t[11:16] + " (" + t[5:10] + ")" for t in times[::step]],
            "timestamps": times[::step],
            "temperatures": formatted_temps[::step],
            "humidities": hums[::step],
            "rainfalls": rains[::step],
            "wind_speeds": formatted_winds[::step],
            "aqi_values": aqis[::step] if len(aqis) >= len(times) else [0] * len(times[::step]),
            "temp_unit": "°F" if is_imperial else "°C",
            "speed_unit": "mph" if is_imperial else "km/h"
        }
