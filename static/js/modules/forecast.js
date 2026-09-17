/**
 * SkyCast Hourly & 7-Day Forecast Module
 */
import { formatDayName, formatTimeOnly, getWeatherIconUrl } from '../utils/formatters.js';

export function renderForecast(forecastData) {
    if (!forecastData) return;

    const unit = forecastData.unit || '°C';

    // 1. Render 24-Hour Timeline
    const hourlyContainer = document.getElementById('hourly-timeline-container');
    if (hourlyContainer && forecastData.hourly) {
        hourlyContainer.innerHTML = forecastData.hourly.map(item => `
            <div class="hourly-card">
                <span class="time">${formatTimeOnly(item.time)}</span>
                <img src="${getWeatherIconUrl(item.weather_code)}" alt="${item.condition}">
                <span class="temp">${Math.round(item.temp)}${unit}</span>
                <span class="pop"><i class="fa-solid fa-droplet"></i> ${item.rain_prob}%</span>
            </div>
        `).join('');
    }

    // 2. Render 7-Day Outlook List
    const dailyContainer = document.getElementById('daily-forecast-container');
    if (dailyContainer && forecastData.daily) {
        // Calculate global min and max for progress bar scaling
        const allMins = forecastData.daily.map(d => d.temp_min);
        const allMaxs = forecastData.daily.map(d => d.temp_max);
        const globalMin = Math.min(...allMins);
        const globalMax = Math.max(...allMaxs);
        const range = (globalMax - globalMin) || 1;

        dailyContainer.innerHTML = forecastData.daily.map(item => {
            const leftPct = Math.max(0, Math.min(100, ((item.temp_min - globalMin) / range) * 100));
            const widthPct = Math.max(10, Math.min(100 - leftPct, ((item.temp_max - item.temp_min) / range) * 100));

            return `
                <div class="daily-row">
                    <div class="daily-day-name">${formatDayName(item.date)}</div>
                    <div class="daily-condition">
                        <img src="${getWeatherIconUrl(item.weather_code)}" alt="${item.condition}">
                        <span>${item.condition}</span>
                    </div>
                    <div class="daily-temp-bar-container">
                        <span class="t-min">${Math.round(item.temp_min)}${unit}</span>
                        <div class="temp-progress-track">
                            <div class="temp-progress-fill" style="margin-left: ${leftPct}%; width: ${widthPct}%;"></div>
                        </div>
                        <span class="t-max">${Math.round(item.temp_max)}${unit}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
}
