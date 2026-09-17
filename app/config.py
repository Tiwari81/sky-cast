import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'skycast_default_secret_key_2026')
    
    # MySQL settings
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'skycast_db')
    
    # SQLite settings
    USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1', 't')
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'skycast.db')
    
    # External API defaults (Open-Meteo)
    OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_REVERSE_GEO_URL = "https://nominatim.openstreetmap.org/reverse"
    OPEN_METEO_HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
