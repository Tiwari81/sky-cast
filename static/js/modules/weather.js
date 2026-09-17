/**
 * SkyCast Current Weather Module
 */
import { formatDateString, getWeatherIconUrl } from '../utils/formatters.js';

export function renderCurrentWeather(data, cityName) {
    if (!data) return;

    document.getElementById('current-city-name').textContent = cityName || data.city_name || 'Current Location';
    document.getElementById('current-date-time').textContent = formatDateString(new Date());

    document.getElementById('current-temp').textContent = Math.round(data.temperature);
    document.getElementById('current-temp-unit').textContent = data.temp_unit;
    document.getElementById('current-condition').textContent = data.condition;
    document.getElementById('current-feels-like').textContent = `Feels like ${Math.round(data.feels_like)}${data.temp_unit}`;

    // Weather Icon
    const iconImg = document.getElementById('weather-icon-img');
    if (iconImg) {
        iconImg.src = getWeatherIconUrl(data.weather_code, data.is_day);
    }

    // Secondary Metrics
    document.getElementById('metric-humidity').textContent = `${data.humidity}%`;
    document.getElementById('metric-pressure').textContent = `${Math.round(data.pressure_hpa)} hPa`;
    document.getElementById('metric-visibility').textContent = `${data.visibility_km} km`;
    document.getElementById('metric-clouds').textContent = `${data.cloud_cover}%`;
    document.getElementById('metric-dewpoint').textContent = `${data.dew_point}${data.temp_unit}`;
    document.getElementById('metric-uv').textContent = data.uv_index;

    // Sun & Moon cycles
    if (data.sun) {
        document.getElementById('sun-sunrise').textContent = data.sun.sunrise.includes('T') ? data.sun.sunrise.split('T')[1] : data.sun.sunrise;
        document.getElementById('sun-sunset').textContent = data.sun.sunset.includes('T') ? data.sun.sunset.split('T')[1] : data.sun.sunset;
    }
    if (data.moon) {
        document.getElementById('moon-phase').textContent = data.moon.phase_name;
        document.getElementById('moon-illumination').textContent = `${data.moon.illumination}%`;
    }

    // Apply Atmospheric Weather Animation (Rain, Lightning, Snow, Clouds)
    applyWeatherAtmosphereEffect(data.weather_code);
}

function applyWeatherAtmosphereEffect(code) {
    const overlay = document.getElementById('weather-atmosphere-overlay');
    if (!overlay) return;

    // Clear previous effect particles
    overlay.innerHTML = '';
    overlay.className = 'weather-atmosphere-overlay';

    // Thunderstorm & Lightning (WMO 95, 96, 99)
    if ([95, 96, 99].includes(code)) {
        overlay.classList.add('weather-effect-thunderstorm', 'weather-effect-rain');
        createRainDrops(overlay, 35);
    }
    // Rain / Drizzle / Showers (WMO 51, 53, 55, 61, 63, 65, 80, 81, 82)
    else if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) {
        overlay.classList.add('weather-effect-rain');
        createRainDrops(overlay, 25);
    }
    // Snow (WMO 71, 73, 75, 77, 85, 86)
    else if ([71, 73, 75, 77, 85, 86].includes(code)) {
        overlay.classList.add('weather-effect-snow');
        createSnowFlakes(overlay, 20);
    }
    // Clouds & Fog (WMO 2, 3, 45, 48)
    else if ([2, 3, 45, 48].includes(code)) {
        overlay.classList.add('weather-effect-clouds');
    }
}

function createRainDrops(container, count) {
    for (let i = 0; i < count; i++) {
        const drop = document.createElement('div');
        drop.className = 'drop';
        drop.style.left = `${Math.random() * 100}%`;
        drop.style.animationDuration = `${0.5 + Math.random() * 0.4}s`;
        drop.style.animationDelay = `${Math.random() * 2}s`;
        container.appendChild(drop);
    }
}

function createSnowFlakes(container, count) {
    for (let i = 0; i < count; i++) {
        const flake = document.createElement('div');
        flake.className = 'flake';
        const size = 3 + Math.random() * 5;
        flake.style.width = `${size}px`;
        flake.style.height = `${size}px`;
        flake.style.left = `${Math.random() * 100}%`;
        flake.style.animationDuration = `${2.5 + Math.random() * 2}s`;
        flake.style.animationDelay = `${Math.random() * 3}s`;
        container.appendChild(flake);
    }
}
