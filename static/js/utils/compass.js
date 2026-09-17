/**
 * SkyCast Wind Compass Helper
 */

export function getWindCardinalDirection(degrees) {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round((degrees % 360) / 22.5) % 16;
    return directions[index];
}

export function updateCompassNeedle(deg) {
    const arrow = document.getElementById('compass-arrow');
    if (arrow) {
        arrow.style.transform = `rotate(${deg}deg)`;
    }
}
