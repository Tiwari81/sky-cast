/**
 * SkyCast Leaflet Interactive Map Module
 */

let mapInstance = null;
let currentMarker = null;
let standardTileLayer = null;
let darkTileBaseLayer = null;
let darkTileRefLayer = null;
let onLocationSelectCallback = null;

export function initMap(initialLat, initialLon, onLocationSelect) {
    onLocationSelectCallback = onLocationSelect;
    const mapContainer = document.getElementById('map');
    if (!mapContainer || mapInstance) return;

    mapInstance = L.map('map', {
        center: [initialLat, initialLon],
        zoom: 10,
        zoomControl: true
    });

    standardTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    });

    darkTileBaseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16,
        attribution: 'Tiles &copy; Esri'
    });

    darkTileRefLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16,
        pane: 'labelsPane'
    });

    // Create custom labels pane so place names render over map
    mapInstance.createPane('labelsPane');
    mapInstance.getPane('labelsPane').style.zIndex = 450;
    mapInstance.getPane('labelsPane').style.pointerEvents = 'none';

    // Add Dark Base + Reference Labels by default
    darkTileBaseLayer.addTo(mapInstance);
    darkTileRefLayer.addTo(mapInstance);

    // Tile Switcher Handlers
    document.getElementById('map-tile-standard')?.addEventListener('click', () => {
        if (mapInstance.hasLayer(darkTileBaseLayer)) mapInstance.removeLayer(darkTileBaseLayer);
        if (mapInstance.hasLayer(darkTileRefLayer)) mapInstance.removeLayer(darkTileRefLayer);
        standardTileLayer.addTo(mapInstance);
    });

    document.getElementById('map-tile-dark')?.addEventListener('click', () => {
        if (mapInstance.hasLayer(standardTileLayer)) mapInstance.removeLayer(standardTileLayer);
        darkTileBaseLayer.addTo(mapInstance);
        darkTileRefLayer.addTo(mapInstance);
    });

    // Map Click Listener to change location
    mapInstance.on('click', (e) => {
        const { lat, lng } = e.latlng;
        if (onLocationSelectCallback) {
            onLocationSelectCallback(lat, lng);
        }
    });
}

export function updateMapLocation(lat, lon, cityName, temp, condition) {
    if (!mapInstance) {
        initMap(lat, lon);
    } else {
        mapInstance.setView([lat, lon], 10);
    }
    updateMapMarker(lat, lon, cityName, temp, condition);
}

function updateMapMarker(lat, lon, cityName = 'Location', temp = '', condition = '') {
    if (currentMarker && mapInstance) {
        mapInstance.removeLayer(currentMarker);
    }

    const labelHtml = `
        <div class="custom-map-pin-badge">
            <span class="pin-city">${cityName}</span>
            ${temp ? `<span class="pin-temp">${temp}</span>` : ''}
            ${condition ? `<span class="pin-cond">${condition}</span>` : ''}
        </div>
    `;

    const customIcon = L.divIcon({
        className: 'custom-map-div-icon',
        html: `<div class="pulse-marker-dot"></div>${labelHtml}`,
        iconSize: [160, 60],
        iconAnchor: [80, 20]
    });

    currentMarker = L.marker([lat, lon], { icon: customIcon }).addTo(mapInstance);

    const popupHtml = `
        <div style="color: #0F172A; text-align: center; font-family: sans-serif; padding: 6px;">
            <strong style="font-size: 1.15em; color: #0284C7;">${cityName}</strong><br>
            ${temp ? `<span style="font-size: 1.4em; font-weight: 800; color: #0F172A;">${temp}</span>` : ''}
            ${condition ? `<br><span style="font-size: 0.9em; color: #475569;">${condition}</span>` : ''}
        </div>
    `;
    currentMarker.bindPopup(popupHtml);
}
