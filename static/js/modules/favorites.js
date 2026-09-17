/**
 * SkyCast Favorite Locations Module
 */
import { fetchFavorites, saveFavorite, removeFavorite } from '../api.js';

let currentFavorites = [];
let onFavoriteSelectCallback = null;

export function initFavorites(onSelect) {
    onFavoriteSelectCallback = onSelect;

    const modal = document.getElementById('favorites-modal');
    const toggleBtn = document.getElementById('favorites-toggle-btn');
    const closeBtn = document.getElementById('favorites-modal-close');

    if (toggleBtn && modal) {
        toggleBtn.addEventListener('click', () => {
            modal.classList.add('active');
            loadAndRenderFavorites();
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    modal?.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });
}

export async function loadAndRenderFavorites() {
    try {
        const res = await fetchFavorites();
        if (res.success) {
            if (res.guest) {
                // Read from localStorage for guest
                currentFavorites = JSON.parse(localStorage.getItem('skycast_guest_favs') || '[]');
            } else {
                currentFavorites = res.favorites || [];
            }
        }
    } catch (e) {
        currentFavorites = JSON.parse(localStorage.getItem('skycast_guest_favs') || '[]');
    }

    renderFavoritesList();
}

function renderFavoritesList() {
    const container = document.getElementById('favorites-list-container');
    if (!container) return;

    if (currentFavorites.length === 0) {
        container.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 1rem;">No saved favorite locations yet. Click the heart icon on any city to save!</p>`;
        return;
    }

    container.innerHTML = currentFavorites.map(fav => `
        <div class="search-item" style="border-radius: var(--border-radius-sm); border: 1px solid rgba(255,255,255,0.1);">
            <div class="fav-item-click" data-lat="${fav.latitude}" data-lon="${fav.longitude}" data-name="${fav.city_name}" style="flex:1;">
                <div class="city-name"><i class="fa-solid fa-location-dot" style="color: var(--accent-blue); margin-right: 6px;"></i> ${fav.city_name}</div>
                <div class="country-name">${fav.country || ''}</div>
            </div>
            <button class="remove-fav-btn icon-btn" data-city="${fav.city_name}" style="width: 32px; height: 32px; font-size: 0.8rem; color: var(--accent-rose);">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
    `).join('');

    // Attach click handlers
    container.querySelectorAll('.fav-item-click').forEach(item => {
        item.addEventListener('click', () => {
            const lat = parseFloat(item.dataset.lat);
            const lon = parseFloat(item.dataset.lon);
            const name = item.dataset.name;
            if (onFavoriteSelectCallback) {
                onFavoriteSelectCallback(lat, lon, name);
                document.getElementById('favorites-modal').classList.remove('active');
            }
        });
    });

    container.querySelectorAll('.remove-fav-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const cityName = btn.dataset.city;
            await deleteFavoriteLocation(cityName);
        });
    });
}

export async function toggleCurrentFavorite(cityName, country, lat, lon) {
    const isSaved = currentFavorites.some(f => f.city_name.toLowerCase() === cityName.toLowerCase());
    if (isSaved) {
        await deleteFavoriteLocation(cityName);
    } else {
        await saveFavoriteLocation(cityName, country, lat, lon);
    }
}

async function saveFavoriteLocation(cityName, country, lat, lon) {
    try {
        const res = await saveFavorite(cityName, country, lat, lon);
        if (res.guest) {
            let favs = JSON.parse(localStorage.getItem('skycast_guest_favs') || '[]');
            if (!favs.some(f => f.city_name.toLowerCase() === cityName.toLowerCase())) {
                favs.push({ city_name: cityName, country, latitude: lat, longitude: lon });
                localStorage.setItem('skycast_guest_favs', JSON.stringify(favs));
            }
        }
        await loadAndRenderFavorites();
        updateHeartIcon(cityName);
    } catch (e) {
        console.error(e);
    }
}

async function deleteFavoriteLocation(cityName) {
    try {
        await removeFavorite(cityName);
        let favs = JSON.parse(localStorage.getItem('skycast_guest_favs') || '[]');
        favs = favs.filter(f => f.city_name.toLowerCase() !== cityName.toLowerCase());
        localStorage.setItem('skycast_guest_favs', JSON.stringify(favs));
        
        await loadAndRenderFavorites();
        updateHeartIcon(cityName);
    } catch (e) {
        console.error(e);
    }
}

export function updateHeartIcon(currentCityName) {
    const heartIcon = document.getElementById('favorite-heart-icon');
    if (!heartIcon) return;
    const isSaved = currentFavorites.some(f => f.city_name.toLowerCase() === currentCityName.toLowerCase());
    if (isSaved) {
        heartIcon.className = 'fa-solid fa-heart';
        heartIcon.style.color = '#F43F5E';
    } else {
        heartIcon.className = 'fa-far fa-heart';
        heartIcon.style.color = 'inherit';
    }
}
