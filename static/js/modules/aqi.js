/**
 * SkyCast Air Quality Module
 */

export function renderAQI(aqiData) {
    if (!aqiData) return;

    const numElem = document.getElementById('aqi-num');
    const circleElem = document.getElementById('aqi-score-circle');
    const titleElem = document.getElementById('aqi-category-title');
    const recElem = document.getElementById('aqi-recommendation');

    if (numElem) numElem.textContent = aqiData.aqi;
    if (titleElem) {
        titleElem.textContent = aqiData.category;
        titleElem.style.color = aqiData.color;
    }
    if (circleElem) {
        circleElem.style.borderColor = aqiData.color;
        circleElem.style.boxShadow = `0 0 20px ${aqiData.color}50`;
    }
    if (recElem) recElem.textContent = aqiData.health_recommendation;

    // Render pollutants
    const p = aqiData.pollutants || {};
    document.getElementById('pol-pm25').textContent = `${p.pm2_5} µg/m³`;
    document.getElementById('pol-pm10').textContent = `${p.pm10} µg/m³`;
    document.getElementById('pol-no2').textContent = `${p.no2} µg/m³`;
    document.getElementById('pol-o3').textContent = `${p.o3} µg/m³`;
    document.getElementById('pol-so2').textContent = `${p.so2} µg/m³`;
    document.getElementById('pol-co').textContent = `${p.co} µg/m³`;
}
