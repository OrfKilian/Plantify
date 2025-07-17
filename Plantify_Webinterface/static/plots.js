// Load Plotly graphs and latest measurements via backend routes

function loadPlots() {
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
        
        // Use backend route instead of direct API call
        fetch(`/api/plots/${plot}?pot_id=${potId}`)
            .then(r => {
                if (!r.ok) {
                    throw new Error(`HTTP error! status: ${r.status}`);
                }
                return r.text();
            })
            .then(html => {
                el.innerHTML = html;
            })
            .catch(err => {
                console.error('Failed to load plot', plot, err);
                el.innerHTML = '<p>Error loading plot data</p>';
            });
    });
}

function loadLatestValues() {
    const rows = document.querySelectorAll('#care-guidelines tbody tr');
    rows.forEach(row => {
        const id = row.dataset.potId;
        if (!id) return;
        
        // Use backend route instead of direct API call
        fetch(`/api/data/latest-value/${id}`)
            .then(r => {
                if (!r.ok) {
                    throw new Error(`HTTP error! status: ${r.status}`);
                }
                return r.json();
            })
            .then(d => {
                // Handle both array and object responses
                const data = Array.isArray(d) ? d[0] : d;
                if (data) {
                    const tempEl = row.querySelector('.val-temp');
                    const airEl = row.querySelector('.val-air');
                    const soilEl = row.querySelector('.val-soil');
                    
                    if (tempEl && data.temperature !== undefined) {
                        tempEl.textContent = parseFloat(data.temperature).toFixed(1);
                    }
                    if (airEl && data.air_humidity !== undefined) {
                        airEl.textContent = parseFloat(data.air_humidity).toFixed(1);
                    }
                    if (soilEl && data.soil_moisture !== undefined) {
                        soilEl.textContent = parseFloat(data.soil_moisture).toFixed(1);
                    }
                }
            })
            .catch(err => {
                console.error('Failed to load latest values for pot', id, err);
                // Set fallback values
                const tempEl = row.querySelector('.val-temp');
                const airEl = row.querySelector('.val-air');
                const soilEl = row.querySelector('.val-soil');
                
                if (tempEl) tempEl.textContent = 'N/A';
                if (airEl) airEl.textContent = 'N/A';
                if (soilEl) soilEl.textContent = 'N/A';
            });
    });
}

function loadTodayData(potId) {
    return fetch(`/api/data/all-today/${potId}`)
        .then(r => {
            if (!r.ok) {
                throw new Error(`HTTP error! status: ${r.status}`);
            }
            return r.json();
        })
        .catch(err => {
            console.error('Failed to load today data for pot', potId, err);
            return [];
        });
}

function loadSunlightData(potId) {
    return fetch(`/api/data/sunlight-30days/${potId}`)
        .then(r => {
            if (!r.ok) {
                throw new Error(`HTTP error! status: ${r.status}`);
            }
            return r.json();
        })
        .catch(err => {
            console.error('Failed to load sunlight data for pot', potId, err);
            return [];
        });
}

function loadAverageData(potId) {
    return fetch(`/api/data/average-mtd/${potId}`)
        .then(r => {
            if (!r.ok) {
                throw new Error(`HTTP error! status: ${r.status}`);
            }
            return r.json();
        })
        .catch(err => {
            console.error('Failed to load average data for pot', potId, err);
            return {};
        });
}

document.addEventListener('DOMContentLoaded', () => {
    loadPlots();
    loadLatestValues();
    
    // Load additional data if needed
    const potId = new URLSearchParams(window.location.search).get('pot_id') || '1';
    
    // Example usage of the new data loading functions
    loadTodayData(potId).then(data => {
        console.log('Today data loaded:', data);
    });
    
    loadSunlightData(potId).then(data => {
        console.log('Sunlight data loaded:', data);
    });
    
    loadAverageData(potId).then(data => {
        console.log('Average data loaded:', data);
    });
});
