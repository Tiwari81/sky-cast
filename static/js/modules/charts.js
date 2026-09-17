/**
 * SkyCast Interactive Chart.js Module
 */

let chartInstance = null;
let currentAnalyticsData = null;
let activeTab = 'temp';

export function initCharts() {
    const ctx = document.getElementById('analyticsChart');
    if (!ctx) return;

    // Attach Tab Event Listeners
    ['temp', 'aqi', 'humidity', 'wind', 'rain'].forEach(type => {
        const btn = document.getElementById(`chart-tab-${type}`);
        if (btn) {
            btn.addEventListener('click', () => {
                document.querySelectorAll('[id^="chart-tab-"]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeTab = type;
                updateChartDisplay();
            });
        }
    });
}

export function renderAnalyticsChart(analyticsData) {
    currentAnalyticsData = analyticsData;
    updateChartDisplay();
}

function updateChartDisplay() {
    if (!currentAnalyticsData) return;

    const ctx = document.getElementById('analyticsChart');
    if (!ctx) return;

    let datasetLabel = 'Temperature';
    let dataValues = currentAnalyticsData.temperatures || [];
    let borderColor = '#38BDF8';
    let backgroundColor = 'rgba(56, 189, 248, 0.15)';
    let unit = currentAnalyticsData.temp_unit || '°C';

    if (activeTab === 'aqi') {
        datasetLabel = 'US Air Quality Index (AQI)';
        dataValues = currentAnalyticsData.aqi_values || [];
        borderColor = '#10B981';
        backgroundColor = 'rgba(16, 185, 129, 0.15)';
        unit = 'AQI';
    } else if (activeTab === 'humidity') {
        datasetLabel = 'Relative Humidity';
        dataValues = currentAnalyticsData.humidities || [];
        borderColor = '#8B5CF6';
        backgroundColor = 'rgba(139, 92, 246, 0.15)';
        unit = '%';
    } else if (activeTab === 'wind') {
        datasetLabel = 'Wind Speed';
        dataValues = currentAnalyticsData.wind_speeds || [];
        borderColor = '#F59E0B';
        backgroundColor = 'rgba(245, 158, 11, 0.15)';
        unit = currentAnalyticsData.speed_unit || 'km/h';
    } else if (activeTab === 'rain') {
        datasetLabel = 'Precipitation / Rainfall';
        dataValues = currentAnalyticsData.rainfalls || [];
        borderColor = '#06B6D4';
        backgroundColor = 'rgba(6, 182, 212, 0.25)';
        unit = 'mm';
    }

    if (chartInstance) {
        chartInstance.destroy();
    }

    const labels = currentAnalyticsData.labels || [];

    chartInstance = new Chart(ctx, {
        type: activeTab === 'rain' ? 'bar' : 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${datasetLabel} (${unit})`,
                data: dataValues,
                borderColor: borderColor,
                backgroundColor: backgroundColor,
                borderWidth: 3,
                fill: true,
                tension: 0.35,
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 12 } }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} ${unit}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748B', font: { size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    ticks: { color: '#94A3B8', font: { size: 11 } }
                }
            }
        }
    });
}
