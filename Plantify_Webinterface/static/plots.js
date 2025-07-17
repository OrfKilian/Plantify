// Load Plotly graphs and latest measurements from plantify_api

function loadPlots(baseUrl) {
    const potId = new URLSearchParams(window.location.search).get('pot_id') || '1';
    const map = {
        'plot-sun': 'sunlight',
        'plot-temp': 'temperature',
        'plot-soil': 'soil',
        'plot-air': 'luftfeuchtigkeit'
    };
    Object.entries(map).forEach(([elementId, plot]) => {
        const el = document.getElementById(elementId);
        if (!el) return;
        fetch(`${baseUrl}/plots/${plot}?pot_id=${potId}`)
            .then(r => r.text())
            .then(html => {
                el.innerHTML = html;
            })
            .catch(err => console.error('Failed to load plot', plot, err));
    });
}

function loadLatestValues(baseUrl) {
    const rows = document.querySelectorAll('#care-guidelines tbody tr');
    rows.forEach(row => {
        const id = row.dataset.potId;
        if (!id) return;
        fetch(`${baseUrl}/latest-value?pot_id=${id}`)
            .then(r => r.json())
            .then(d => {
                row.querySelector('.val-temp').textContent = parseFloat(d.temperature).toFixed(1);
                row.querySelector('.val-air').textContent = parseFloat(d.air_humidity).toFixed(1);
                row.querySelector('.val-soil').textContent = parseFloat(d.soil_moisture).toFixed(1);
            })
            .catch(err => console.error('Failed to load latest values', err));
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const apiBase = 'http://localhost:5001';
    loadPlots(apiBase);
    loadLatestValues(apiBase);
});
