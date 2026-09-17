/**
 * SkyCast Weather Alerts Module
 */

export function renderAlerts(alertsList) {
    const container = document.getElementById('alerts-container');
    if (!container) return;

    if (!alertsList || alertsList.length === 0) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = alertsList.map(alert => `
        <div class="alert-item ${alert.badge_class || 'badge-warning'}">
            <div class="alert-icon">
                <i class="fa-solid ${alert.icon || 'fa-triangle-exclamation'}"></i>
            </div>
            <div class="alert-content">
                <h4>[${alert.type.toUpperCase()}] ${alert.title}</h4>
                <p>${alert.message}</p>
            </div>
        </div>
    `).join('');
}
