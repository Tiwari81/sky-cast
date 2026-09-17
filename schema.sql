-- SkyCast MySQL Database Schema

CREATE DATABASE IF NOT EXISTS skycast_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skycast_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    default_city VARCHAR(100) DEFAULT 'London',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Favorite Locations Table
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

-- 3. Weather History Table
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

-- 4. Air Quality History Table
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
