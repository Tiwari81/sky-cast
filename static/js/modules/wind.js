/**
 * SkyCast Wind Module
 */
import { getWindCardinalDirection, updateCompassNeedle } from '../utils/compass.js';

export function renderWind(windData) {
    if (!windData) return;

    const speedVal = document.getElementById('wind-speed-val');
    const dirVal = document.getElementById('wind-dir-val');
    const gustVal = document.getElementById('wind-gust-val');

    if (speedVal) speedVal.textContent = `${windData.speed} ${windData.speed_unit}`;
    if (dirVal) dirVal.textContent = `${windData.direction}° (${getWindCardinalDirection(windData.direction)})`;
    if (gustVal) gustVal.textContent = `${windData.gust} ${windData.speed_unit}`;

    updateCompassNeedle(windData.direction);
}
