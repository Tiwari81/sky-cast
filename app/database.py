import sqlite3
import pymysql
import logging
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    def __init__(self, app=None):
        self.use_sqlite = Config.USE_SQLITE
        self.sqlite_path = Config.SQLITE_DB_PATH
        self.mysql_config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.active_engine = "SQLITE" if self.use_sqlite else "MYSQL"
        self._init_db()

    def _get_mysql_connection(self):
        return pymysql.connect(**self.mysql_config)

    def _get_sqlite_connection(self):
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        # First attempt MySQL if configured
        if not self.use_sqlite:
            try:
                # Try connecting without database first to create DB if needed
                root_config = self.mysql_config.copy()
                db_name = root_config.pop('database')
                conn = pymysql.connect(**root_config)
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.close()

                # Now connect to database and run setup
                conn = self._get_mysql_connection()
                with conn.cursor() as cursor:
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(80) NOT NULL UNIQUE,
                        email VARCHAR(120) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        default_city VARCHAR(100) DEFAULT 'London',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS favorite_locations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        city_name VARCHAR(100) NOT NULL,
                        country VARCHAR(100) DEFAULT '',
                        latitude DECIMAL(10, 6) NOT NULL,
                        longitude DECIMAL(10, 6) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        UNIQUE KEY user_city_unique (user_id, city_name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        city_name VARCHAR(100) NOT NULL,
                        latitude DECIMAL(10, 6) NOT NULL,
                        longitude DECIMAL(10, 6) NOT NULL,
                        temp_c FLOAT NOT NULL,
                        condition_text VARCHAR(100) NOT NULL,
                        humidity INT NOT NULL,
                        wind_kph FLOAT NOT NULL,
                        uv_index FLOAT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS aqi_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        city_name VARCHAR(100) NOT NULL,
                        latitude DECIMAL(10, 6) NOT NULL,
                        longitude DECIMAL(10, 6) NOT NULL,
                        aqi_value INT NOT NULL,
                        aqi_category VARCHAR(50) NOT NULL,
                        pm25 FLOAT DEFAULT 0,
                        pm10 FLOAT DEFAULT 0,
                        co FLOAT DEFAULT 0,
                        no2 FLOAT DEFAULT 0,
                        so2 FLOAT DEFAULT 0,
                        o3 FLOAT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                conn.commit()
                conn.close()
                self.active_engine = "MYSQL"
                logger.info("Successfully connected to MySQL Database!")
                return
            except Exception as e:
                logger.warning(f"MySQL connection failed ({e}). Falling back to SQLite engine ({self.sqlite_path}).")
                self.use_sqlite = True

        # SQLite Fallback Engine Initialization
        self.active_engine = "SQLITE"
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            default_city TEXT DEFAULT 'London',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorite_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            city_name TEXT NOT NULL,
            country TEXT DEFAULT '',
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, city_name)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            temp_c REAL NOT NULL,
            condition_text TEXT NOT NULL,
            humidity INTEGER NOT NULL,
            wind_kph REAL NOT NULL,
            uv_index REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS aqi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            aqi_value INTEGER NOT NULL,
            aqi_category TEXT NOT NULL,
            pm25 REAL DEFAULT 0,
            pm10 REAL DEFAULT 0,
            co REAL DEFAULT 0,
            no2 REAL DEFAULT 0,
            so2 REAL DEFAULT 0,
            o3 REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        logger.info(f"Initialized SQLite database at {self.sqlite_path}")

    def execute_query(self, query_sql, params=(), fetch_one=False, fetch_all=False, commit=False):
        """Unified query runner executing against active database engine (MySQL or SQLite)"""
        if self.active_engine == "MYSQL":
            conn = self._get_mysql_connection()
            try:
                with conn.cursor() as cursor:
                    # Replace SQLite style ? placeholder with MySQL %s if needed
                    mysql_sql = query_sql.replace('?', '%s')
                    cursor.execute(mysql_sql, params)
                    if commit:
                        conn.commit()
                        last_id = cursor.lastrowid
                        conn.close()
                        return last_id
                    if fetch_one:
                        res = cursor.fetchone()
                        conn.close()
                        return res
                    if fetch_all:
                        res = cursor.fetchall()
                        conn.close()
                        return res
                    conn.close()
                    return None
            except Exception as e:
                conn.close()
                logger.error(f"MySQL Query Error: {e}")
                raise e
        else:
            conn = self._get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query_sql, params)
                if commit:
                    conn.commit()
                    last_id = cursor.lastrowid
                    conn.close()
                    return last_id
                if fetch_one:
                    row = cursor.fetchone()
                    conn.close()
                    return dict(row) if row else None
                if fetch_all:
                    rows = cursor.fetchall()
                    conn.close()
                    return [dict(r) for r in rows]
                conn.close()
                return None
            except Exception as e:
                conn.close()
                logger.error(f"SQLite Query Error: {e}")
                raise e

db_manager = DatabaseManager()
