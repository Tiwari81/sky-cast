import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(path, method="GET", payload=None, headers=None):
    url = f"{BASE_URL}{path}"
    headers = headers or {}
    data = None
    if payload:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print(f"[OK] [{method}] {path} -> Status {response.status}, Success: {res_json.get('success')}")
            return res_json
    except Exception as e:
        print(f"[FAIL] [{method}] {path} -> Failed: {e}")
        return None

def main():
    print("=== SKYCAST BACKEND API VERIFICATION ===")
    
    # 1. Weather
    weather = test_endpoint("/api/weather?lat=51.5074&lon=-0.1278&city=London")
    assert weather and weather.get("data", {}).get("temperature") is not None

    # 2. Forecast
    forecast = test_endpoint("/api/forecast?lat=51.5074&lon=-0.1278")
    assert forecast and len(forecast.get("data", {}).get("hourly", [])) > 0

    # 3. Air Quality
    aqi = test_endpoint("/api/aqi?lat=51.5074&lon=-0.1278")
    assert aqi and aqi.get("data", {}).get("aqi") is not None

    # 4. Alerts
    alerts = test_endpoint("/api/alerts?lat=51.5074&lon=-0.1278")
    assert alerts and "alerts" in alerts

    # 5. Location Search
    search = test_endpoint("/api/location/search?q=Tokyo")
    assert search and len(search.get("results", [])) > 0

    # 6. History
    history = test_endpoint("/api/history?lat=51.5074&lon=-0.1278")
    assert history and "analytics" in history

    # 7. User Registration & Login
    uname = f"testuser_{int(time.time())}"
    reg = test_endpoint("/api/auth/register", method="POST", payload={
        "username": uname,
        "email": f"{uname}@example.com",
        "password": "Password123!",
        "default_city": "Tokyo"
    })
    assert reg and reg.get("success") is True
    token = reg.get("token")

    # 8. Favorites with Auth Token
    fav_headers = {"Authorization": f"Bearer {token}"}
    add_fav = test_endpoint("/api/favorites", method="POST", payload={
        "city_name": "Tokyo",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503
    }, headers=fav_headers)
    assert add_fav and add_fav.get("success") is True

    get_favs = test_endpoint("/api/favorites", headers=fav_headers)
    assert get_favs and len(get_favs.get("favorites", [])) > 0

    print("\n--- ALL BACKEND REST API ENDPOINTS VERIFIED SUCCESSFULLY! ---")

if __name__ == "__main__":
    main()
