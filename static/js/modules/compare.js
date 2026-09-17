/**
 * SkyCast Multi-City Comparison Module
 */
import { searchLocation, fetchWeather, fetchAQI } from '../api.js';

let comparedCities = [];

export function initCompare() {
    const modal = document.getElementById('compare-modal');
    const toggleBtn = document.getElementById('compare-toggle-btn');
    const closeBtn = document.getElementById('compare-modal-close');
    const addBtn = document.getElementById('compare-add-btn');

    if (toggleBtn && modal) {
        toggleBtn.addEventListener('click', () => {
            modal.classList.add('active');
            renderCompareGrid();
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }

    modal?.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });

    if (addBtn) {
        addBtn.addEventListener('click', async () => {
            const input = document.getElementById('compare-city-input');
            const query = input?.value.trim();
            if (!query) return;

            try {
                const searchRes = await searchLocation(query);
                if (searchRes.results && searchRes.results.length > 0) {
                    const first = searchRes.results[0];
                    await addCityToComparison(first.name, first.latitude, first.longitude);
                    if (input) input.value = '';
                } else {
                    alert('City not found. Please try another name.');
                }
            } catch (e) {
                console.error(e);
            }
        });
    }
}

export async function addCityToComparison(cityName, lat, lon) {
    if (comparedCities.some(c => c.name.toLowerCase() === cityName.toLowerCase())) {
        return;
    }
    if (comparedCities.length >= 4) {
        alert('Maximum 4 cities allowed in comparison grid.');
        return;
    }

    try {
        const weatherRes = await fetchWeather(lat, lon, 'c', cityName);
        const aqiRes = await fetchAQI(lat, lon, cityName);

        if (weatherRes.success) {
            comparedCities.push({
                name: cityName,
                weather: weatherRes.data,
                aqi: aqiRes.data || {}
            });
            renderCompareGrid();
        }
    } catch (e) {
        console.error(e);
    }
}

function renderCompareGrid() {
    const grid = document.getElementById('compare-cities-grid');
    if (!grid) return;

    if (comparedCities.length === 0) {
        grid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 1.5rem;">Enter a city name above to start comparing weather & air quality metrics side by side!</p>`;
        return;
    }

    grid.innerHTML = comparedCities.map((city, idx) => `
        <div class="glass-card" style="position: relative; padding: 1.25rem;">
            <button class="remove-compare-btn icon-btn" data-idx="${idx}" style="position: absolute; top: 10px; right: 10px; width: 28px; height: 28px; font-size: 0.75rem;">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <h4 style="font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--accent-blue);">${city.name}</h4>
            <div style="font-size: 2.2rem; font-weight: 800; font-family: var(--font-heading); margin: 0.4rem 0;">${Math.round(city.weather.temperature)}${city.weather.temp_unit}</div>
            <div style="font-size: 0.9rem; color: var(--text-secondary); font-weight: 600;">${city.weather.condition}</div>
            
            <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 0.75rem; padding-top: 0.75rem; display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.85rem;">
                <div><strong>Feels like:</strong> ${Math.round(city.weather.feels_like)}${city.weather.temp_unit}</div>
                <div><strong>Humidity:</strong> ${city.weather.humidity}%</div>
                <div><strong>Wind Speed:</strong> ${city.weather.wind.speed} ${city.weather.wind.speed_unit}</div>
                <div><strong>AQI:</strong> <span style="color: ${city.aqi.color || 'inherit'}; font-weight: 700;">${city.aqi.aqi || '--'} (${city.aqi.category || '--'})</span></div>
            </div>
        </div>
    `).join('');

    grid.querySelectorAll('.remove-compare-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx);
            comparedCities.splice(idx, 1);
            renderCompareGrid();
        });
    });
}
