/**
 * SkyCast Utility Formatters
 */

export function formatDateString(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

export function formatDayName(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    }
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric' });
}

export function formatTimeOnly(timeString) {
    if (!timeString) return '';
    if (timeString.includes('T')) {
        return timeString.split('T')[1].substring(0, 5);
    }
    return timeString;
}

export function getWeatherIconUrl(wmoCode, isDay = 1) {
    // Map WMO codes to high quality weather icons
    const dayNight = isDay ? 'd' : 'n';
    const codeMap = {
        0: `01${dayNight}`,  // Clear
        1: `02${dayNight}`,  // Mainly clear
        2: `03${dayNight}`,  // Partly cloudy
        3: `04${dayNight}`,  // Overcast
        45: `50${dayNight}`, // Fog
        48: `50${dayNight}`,
        51: `09d`,           // Drizzle
        53: `09d`,
        55: `09d`,
        61: `10${dayNight}`,  // Rain
        63: `10${dayNight}`,
        65: `10d`,
        71: `13d`,           // Snow
        73: `13d`,
        75: `13d`,
        80: `09d`,
        81: `09d`,
        82: `09d`,
        95: `11d`,           // Thunderstorm
        96: `11d`,
        99: `11d`
    };
    const iconCode = codeMap[wmoCode] || `02${dayNight}`;
    return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
}
