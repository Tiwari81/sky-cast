/**
 * SkyCast Centralized API Service
 */

const BASE_URL = '';

function getAuthHeaders() {
    const token = localStorage.getItem('skycast_jwt_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function fetchWeather(lat, lon, units = 'c', city = '') {
    const res = await fetch(`${BASE_URL}/api/weather?lat=${lat}&lon=${lon}&units=${units}&city=${encodeURIComponent(city)}`);
    return await res.json();
}

export async function fetchForecast(lat, lon, units = 'c') {
    const res = await fetch(`${BASE_URL}/api/forecast?lat=${lat}&lon=${lon}&units=${units}`);
    return await res.json();
}

export async function fetchAQI(lat, lon, city = '') {
    const res = await fetch(`${BASE_URL}/api/aqi?lat=${lat}&lon=${lon}&city=${encodeURIComponent(city)}`);
    return await res.json();
}

export async function fetchAlerts(lat, lon, units = 'c') {
    const res = await fetch(`${BASE_URL}/api/alerts?lat=${lat}&lon=${lon}&units=${units}`);
    return await res.json();
}

export async function fetchHistory(lat, lon, days = 7, units = 'c', city = '') {
    const res = await fetch(`${BASE_URL}/api/history?lat=${lat}&lon=${lon}&days=${days}&units=${units}&city=${encodeURIComponent(city)}`);
    return await res.json();
}

export async function searchLocation(query) {
    const res = await fetch(`${BASE_URL}/api/location/search?q=${encodeURIComponent(query)}`);
    return await res.json();
}

export async function reverseGeocode(lat, lon) {
    const res = await fetch(`${BASE_URL}/api/location/reverse?lat=${lat}&lon=${lon}`);
    return await res.json();
}

export async function fetchFavorites() {
    const res = await fetch(`${BASE_URL}/api/favorites`, { headers: getAuthHeaders() });
    return await res.json();
}

export async function saveFavorite(city_name, country, latitude, longitude) {
    const res = await fetch(`${BASE_URL}/api/favorites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        body: JSON.stringify({ city_name, country, latitude, longitude })
    });
    return await res.json();
}

export async function removeFavorite(city_name) {
    const res = await fetch(`${BASE_URL}/api/favorites/${encodeURIComponent(city_name)}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
    });
    return await res.json();
}

export async function registerUser(username, email, password, default_city) {
    const res = await fetch(`${BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, default_city })
    });
    return await res.json();
}

export async function loginUser(username_or_email, password) {
    const res = await fetch(`${BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username_or_email, password })
    });
    return await res.json();
}

export async function fetchCurrentUser() {
    const res = await fetch(`${BASE_URL}/api/auth/me`, { headers: getAuthHeaders() });
    return await res.json();
}
