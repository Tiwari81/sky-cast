/**
 * SkyCast Application Controller
 */
import { fetchWeather, fetchForecast, fetchAQI, fetchAlerts, fetchHistory, searchLocation, reverseGeocode } from './api.js';
import { renderCurrentWeather } from './modules/weather.js';
import { renderForecast } from './modules/forecast.js';
import { renderAQI } from './modules/aqi.js';
import { renderWind } from './modules/wind.js';
import { initCharts, renderAnalyticsChart } from './modules/charts.js';
import { initMap, updateMapLocation } from './modules/map.js';
import { renderAlerts } from './modules/alerts.js';
import { initFavorites, loadAndRenderFavorites, toggleCurrentFavorite, updateHeartIcon } from './modules/favorites.js';
import { initCompare, addCityToComparison } from './modules/compare.js';
import { initAuth } from './modules/auth.js';
import { initSettings, getCurrentUnits } from './modules/settings.js';

// Application State
let currentLat = 51.5074; // London default
let currentLon = -0.1278;
let currentCityName = 'London';
let currentCountry = 'United Kingdom';

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    // 1. Initialize Sub-modules
    initCharts();
    initSettings(
        () => loadCityData(currentLat, currentLon, currentCityName),
        () => {}
    );
    initMap(currentLat, currentLon, (lat, lon) => {
        handleMapLocationClick(lat, lon);
    });
    initFavorites((lat, lon, cityName) => {
        loadCityData(lat, lon, cityName);
    });
    initCompare();
    initAuth((user) => {
        if (user && user.default_city) {
            searchAndLoadCity(user.default_city);
        }
        loadAndRenderFavorites();
    });

    // 2. Attach City Search Handlers
    setupSearchHandlers();

    // 3. Attach Geolocation Handler
    setupGeoHandler();

    // 4. Attach Heart Icon Favorite Button Click
    const favBtn = document.getElementById('add-favorite-btn');
    if (favBtn) {
        favBtn.addEventListener('click', async () => {
            await toggleCurrentFavorite(currentCityName, currentCountry, currentLat, currentLon);
        });
    }

    // 5. Initial Load - Default London or Browser Geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const rev = await reverseGeocode(lat, lon);
                if (rev && rev.data) {
                    loadCityData(lat, lon, rev.data.city, rev.data.country);
                } else {
                    loadCityData(lat, lon, 'Current Location');
                }
            },
            () => {
                loadCityData(currentLat, currentLon, currentCityName, currentCountry);
            },
            { timeout: 5000 }
        );
    } else {
        loadCityData(currentLat, currentLon, currentCityName, currentCountry);
    }

    // Load saved favorites list
    loadAndRenderFavorites();
}

async function loadCityData(lat, lon, cityName = 'Location', country = '') {
    currentLat = lat;
    currentLon = lon;
    currentCityName = cityName;
    currentCountry = country;

    const units = getCurrentUnits();

    try {
        // Parallel multi-fetch for weather, forecast, AQI, alerts, history
        const [weatherRes, forecastRes, aqiRes, alertsRes, historyRes] = await Promise.all([
            fetchWeather(lat, lon, units, cityName),
            fetchForecast(lat, lon, units),
            fetchAQI(lat, lon, cityName),
            fetchAlerts(lat, lon, units),
            fetchHistory(lat, lon, 7, units, cityName)
        ]);

        if (weatherRes.success) {
            renderCurrentWeather(weatherRes.data, cityName);
            renderWind(weatherRes.data.wind);
            updateMapLocation(lat, lon, cityName, `${Math.round(weatherRes.data.temperature)}${weatherRes.data.temp_unit}`, weatherRes.data.condition);
        }

        if (forecastRes.success) {
            renderForecast(forecastRes.data);
        }

        if (aqiRes.success) {
            renderAQI(aqiRes.data);
        }

        if (alertsRes.success) {
            renderAlerts(alertsRes.alerts);
        }

        if (historyRes.success) {
            renderAnalyticsChart(historyRes.analytics);
        }

        // Update heart icon state
        updateHeartIcon(cityName);

    } catch (e) {
        console.error("Error loading environmental data:", e);
    }
}

async function handleMapLocationClick(lat, lon) {
    try {
        const rev = await reverseGeocode(lat, lon);
        const name = (rev && rev.data && rev.data.city) ? rev.data.city : 'Selected Location';
        const country = (rev && rev.data && rev.data.country) ? rev.data.country : '';
        loadCityData(lat, lon, name, country);
    } catch (e) {
        loadCityData(lat, lon, 'Selected Location');
    }
}

function setupSearchHandlers() {
    const input = document.getElementById('city-search-input');
    const dropdown = document.getElementById('search-results-dropdown');
    let debounceTimer = null;

    if (!input || !dropdown) return;

    input.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);

        if (query.length < 2) {
            dropdown.innerHTML = '';
            dropdown.classList.remove('active');
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const res = await searchLocation(query);
                if (res.results && res.results.length > 0) {
                    dropdown.innerHTML = res.results.map(item => `
                        <div class="search-item" data-lat="${item.latitude}" data-lon="${item.longitude}" data-name="${item.name}" data-country="${item.country}">
                            <div>
                                <span class="city-name">${item.name}</span>
                                ${item.admin1 ? `<span style="font-size: 0.8rem; color: var(--text-muted); margin-left: 4px;">(${item.admin1})</span>` : ''}
                            </div>
                            <span class="country-name">${item.country}</span>
                        </div>
                    `).join('');
                    dropdown.classList.add('active');

                    dropdown.querySelectorAll('.search-item').forEach(el => {
                        el.addEventListener('click', () => {
                            const lat = parseFloat(el.dataset.lat);
                            const lon = parseFloat(el.dataset.lon);
                            const name = el.dataset.name;
                            const country = el.dataset.country;

                            input.value = `${name}, ${country}`;
                            dropdown.classList.remove('active');
                            loadCityData(lat, lon, name, country);
                        });
                    });
                } else {
                    dropdown.innerHTML = `<div style="padding: 0.75rem 1.25rem; color: var(--text-muted);">No locations found matching "${query}"</div>`;
                    dropdown.classList.add('active');
                }
            } catch (err) {
                console.error(err);
            }
        }, 300);
    });

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
}

function setupGeoHandler() {
    const geoBtn = document.getElementById('geo-btn');
    if (!geoBtn) return;

    geoBtn.addEventListener('click', () => {
        if (navigator.geolocation) {
            geoBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
            navigator.geolocation.getCurrentPosition(
                async (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const rev = await reverseGeocode(lat, lon);
                    const name = (rev && rev.data && rev.data.city) ? rev.data.city : 'Current Location';
                    const country = (rev && rev.data && rev.data.country) ? rev.data.country : '';
                    
                    geoBtn.innerHTML = `<i class="fa-solid fa-crosshairs"></i>`;
                    loadCityData(lat, lon, name, country);
                },
                (err) => {
                    geoBtn.innerHTML = `<i class="fa-solid fa-crosshairs"></i>`;
                    alert("Could not access your location. Please check browser permissions.");
                },
                { timeout: 8000 }
            );
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    });
}

async function searchAndLoadCity(cityName) {
    try {
        const res = await searchLocation(cityName);
        if (res.results && res.results.length > 0) {
            const first = res.results[0];
            loadCityData(first.latitude, first.longitude, first.name, first.country);
        }
    } catch (e) {
        console.error(e);
    }
}
