/**
 * SkyCast Settings & Unit Preferences Module
 */

let currentUnits = localStorage.getItem('skycast_units') || 'c';
let currentTheme = localStorage.getItem('skycast_theme') || 'dark';

export function initSettings(onUnitsChanged, onThemeChanged) {
    // Apply saved theme on initial boot
    applyTheme(currentTheme);

    const themeBtn = document.getElementById('theme-toggle-btn');
    const unitBtn = document.getElementById('unit-toggle-btn');

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            currentTheme = (currentTheme === 'dark') ? 'light' : 'dark';
            localStorage.setItem('skycast_theme', currentTheme);
            applyTheme(currentTheme);
            if (onThemeChanged) onThemeChanged(currentTheme);
        });
    }

    if (unitBtn) {
        unitBtn.addEventListener('click', () => {
            currentUnits = (currentUnits === 'c') ? 'f' : 'c';
            localStorage.setItem('skycast_units', currentUnits);
            updateUnitText();
            if (onUnitsChanged) onUnitsChanged(currentUnits);
        });
    }

    updateUnitText();
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.getElementById('theme-icon');
    const label = document.getElementById('theme-text-label');
    if (icon) {
        icon.className = (theme === 'dark') ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
        icon.style.color = (theme === 'dark') ? '#38BDF8' : '#F59E0B';
    }
    if (label) {
        label.textContent = (theme === 'dark') ? 'Dark Mode' : 'Light Mode';
    }
}

function updateUnitText() {
    const text = document.getElementById('unit-toggle-text');
    if (text) {
        text.textContent = (currentUnits === 'c') ? '°C Metric' : '°F Imperial';
    }
}

export function getCurrentUnits() {
    return currentUnits;
}

export function getCurrentTheme() {
    return currentTheme;
}
