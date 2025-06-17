/**
 * Advanced Dutch Green Space Dashboard
 * Main application script
 */

// Configuration
const CONFIG = {
    mapbox: {
        // API key loaded from external config.js file
        accessToken: window.CONFIG_SECRETS?.mapbox?.accessToken || 'YOUR_MAPBOX_TOKEN_HERE',
        style: 'mapbox://styles/mapbox/light-v11',
        center: [5.2913, 52.1326], // Netherlands center
        zoom: 7,
        pitch: 0,
        bearing: 0
    },
    api: {
        baseUrl: window.location.origin,
        endpoints: {
            data: '/api/green_space_advanced',
            stats: '/api/statistics'
        }
    }
};

// Global state
const state = {
    map: null,
    data: null,
    statistics: null,
    selectedPostcode: null,
    is3D: false,
    currentChart: 'total_greenery'
};

/**
 * Main Application Class
 */
class GreenSpaceDashboard {
    constructor() {
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Green Space Dashboard...');
        
        try {
            // Initialize components in sequence
            await this.loadData();
            await this.initMap();
            this.initTabs();
            this.initControls();
            this.initLegend();
            await this.loadStatistics();
            this.initChart();
            
            console.log('✅ Dashboard initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize dashboard:', error);
            this.showError('Failed to load dashboard. Please check the server connection.');
        }
    }

    async loadData() {
        console.log('📊 Loading green space data...');
        
        try {
            const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.data}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            state.data = await response.json();
            console.log(`✅ Loaded ${state.data.features.length} postcode areas`);
        } catch (error) {
            console.error('Failed to load data:', error);
            throw error;
        }
    }

    async initMap() {
        console.log('🗺️ Initializing map...');
        
        // Note: For demo purposes, we'll use a public token or handle gracefully
        mapboxgl.accessToken = CONFIG.mapbox.accessToken;
        
        state.map = new mapboxgl.Map({
            container: 'map',
            style: CONFIG.mapbox.style,
            center: CONFIG.mapbox.center,
            zoom: CONFIG.mapbox.zoom,
            pitch: CONFIG.mapbox.pitch,
            bearing: CONFIG.mapbox.bearing,
            antialias: true
        });

        state.map.on('load', () => {
            this.addDataLayers();
            this.setupMapInteractions();
        });

        // Add navigation controls
        state.map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    }

    addDataLayers() {
        // Add the GeoJSON data as a source
        state.map.addSource('green-space', {
            type: 'geojson',
            data: state.data
        });

        // Add fill layer with trivariate colors
        state.map.addLayer({
            id: 'green-space-fill',
            type: 'fill',
            source: 'green-space',
            paint: {
                'fill-color': ['get', 'color'],
                'fill-opacity': 0.8
            }
        });

        // Add stroke layer
        state.map.addLayer({
            id: 'green-space-stroke',
            type: 'line',
            source: 'green-space',
            paint: {
                'line-color': '#ffffff',
                'line-width': 0.5,
                'line-opacity': 0.6
            }
        });

        // Add hover effect layer
        state.map.addLayer({
            id: 'green-space-hover',
            type: 'line',
            source: 'green-space',
            paint: {
                'line-color': '#ff6b35',
                'line-width': 3,
                'line-opacity': 1
            },
            filter: ['==', 'PC4', '']
        });
    }

    setupMapInteractions() {
        let hoveredPostcode = null;

        // Mouse enter - highlight
        state.map.on('mouseenter', 'green-space-fill', (e) => {
            state.map.getCanvas().style.cursor = 'pointer';
            
            if (e.features.length > 0) {
                hoveredPostcode = e.features[0].properties.PC4;
                state.map.setFilter('green-space-hover', ['==', 'PC4', hoveredPostcode]);
            }
        });

        // Mouse leave - remove highlight
        state.map.on('mouseleave', 'green-space-fill', () => {
            state.map.getCanvas().style.cursor = '';
            state.map.setFilter('green-space-hover', ['==', 'PC4', '']);
            hoveredPostcode = null;
        });

        // Click - select postcode
        state.map.on('click', 'green-space-fill', (e) => {
            if (e.features.length > 0) {
                const feature = e.features[0];
                this.selectPostcode(feature.properties.PC4, feature.properties);
            }
        });
    }

    selectPostcode(pc4, properties) {
        state.selectedPostcode = { pc4, properties };
        console.log('📍 Selected postcode:', pc4);
        
        // Update details panel
        this.updateDetailsPanel(properties);
        
        // Switch to details tab if not already there
        if (!document.querySelector('.tab[data-tab="details"]').classList.contains('active')) {
            this.switchTab('details');
        }
    }

    toggle3D() {
        state.is3D = !state.is3D;
        
        if (state.is3D) {
            // Add 3D extrusion layer
            state.map.addLayer({
                id: 'green-space-3d',
                type: 'fill-extrusion',
                source: 'green-space',
                paint: {
                    'fill-extrusion-color': ['get', 'color'],
                    'fill-extrusion-height': [
                        'interpolate',
                        ['linear'],
                        ['get', 'total_greenery'],
                        0, 0,
                        150, 3000
                    ],
                    'fill-extrusion-opacity': 0.8
                }
            });
            
            // Hide the 2D fill layer
            state.map.setLayoutProperty('green-space-fill', 'visibility', 'none');
            
            // Update map pitch for better 3D view
            state.map.easeTo({ pitch: 45, bearing: -17.6 });
        } else {
            // Remove 3D layer and show 2D
            if (state.map.getLayer('green-space-3d')) {
                state.map.removeLayer('green-space-3d');
            }
            state.map.setLayoutProperty('green-space-fill', 'visibility', 'visible');
            state.map.easeTo({ pitch: 0, bearing: 0 });
        }
    }

    initTabs() {
        const tabs = document.querySelectorAll('.tab');
        const contents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
                this.switchTab(targetTab);
            });
        });
    }

    switchTab(targetTab) {
        // Remove active class from all tabs and contents
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Add active class to target tab and content
        document.querySelector(`[data-tab="${targetTab}"]`).classList.add('active');
        document.getElementById(`${targetTab}-content`).classList.add('active');
    }

    initControls() {
        // Reset view button
        document.getElementById('resetView').addEventListener('click', () => {
            state.map.easeTo({
                center: CONFIG.mapbox.center,
                zoom: CONFIG.mapbox.zoom,
                pitch: CONFIG.mapbox.pitch,
                bearing: CONFIG.mapbox.bearing
            });
        });

        // Toggle 3D button
        document.getElementById('toggleHeight').addEventListener('click', () => {
            this.toggle3D();
        });

        // Clear selection button
        document.getElementById('clearSelection').addEventListener('click', () => {
            state.selectedPostcode = null;
            this.clearDetailsPanel();
        });

        // Chart control buttons
        document.querySelectorAll('.chart-control').forEach(control => {
            control.addEventListener('click', (e) => {
                document.querySelectorAll('.chart-control').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                state.currentChart = e.target.dataset.x;
                this.updateChart();
            });
        });
    }

    initLegend() {
        const legendGrid = document.getElementById('legendGrid');
        
        // Create 3x3 grid for trivariate legend
        for (let bushes = 2; bushes >= 0; bushes--) {
            for (let trees = 0; trees < 3; trees++) {
                const cell = document.createElement('div');
                cell.className = 'legend-cell';
                
                // Calculate RGB based on position
                const r = Math.round((trees / 2) * 255);
                const g = Math.round((bushes / 2) * 255);
                const b = Math.round((2 - trees - bushes) / 2 * 255);
                
                cell.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
                legendGrid.appendChild(cell);
            }
        }
    }

    async loadStatistics() {
        console.log('📈 Loading statistics...');
        
        try {
            const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.stats}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            state.statistics = await response.json();
            this.updateStatisticsPanel();
        } catch (error) {
            console.error('Failed to load statistics:', error);
            this.showError('Failed to load statistics');
        }
    }

    updateStatisticsPanel() {
        const panel = document.querySelector('.stats-panel');
        const stats = state.statistics;
        
        panel.innerHTML = `
            <div class="stat-group">
                <h3>Dataset Overview</h3>
                <div class="stat-item">
                    <span class="stat-label">Total Postcodes</span>
                    <span class="stat-value">${stats.total_postcodes.toLocaleString()}</span>
                </div>
            </div>

            <div class="stat-group">
                <h3>Green Space Distribution</h3>
                <div class="stat-item">
                    <span class="stat-label">Trees (avg)</span>
                    <span class="stat-value">${stats.greenery_stats.trees.mean.toFixed(1)}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Bushes (avg)</span>
                    <span class="stat-value">${stats.greenery_stats.bushes.mean.toFixed(1)}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Grass (avg)</span>
                    <span class="stat-value">${stats.greenery_stats.grass.mean.toFixed(1)}%</span>
                </div>
            </div>

            <div class="stat-group">
                <h3>Calculated Metrics</h3>
                <div class="stat-item">
                    <span class="stat-label">Total Green (range)</span>
                    <span class="stat-value">${stats.total_greenery.min.toFixed(1)}% - ${stats.total_greenery.max.toFixed(1)}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Balance Score (avg)</span>
                    <span class="stat-value">${stats.balance_score.mean.toFixed(2)}</span>
                </div>
            </div>

            ${stats.cbs_data ? `
                <div class="stat-group">
                    <h3>CBS Data Integration</h3>
                    ${Object.entries(stats.cbs_data).map(([key, data]) => `
                        <div class="stat-item">
                            <span class="stat-label">${key.replace(/_/g, ' ')}</span>
                            <span class="stat-value">${data.available_records.toLocaleString()} records</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
    }

    initChart() {
        this.updateChart();
    }

    updateChart() {
        if (!state.data) return;

        const features = state.data.features;
        const xField = state.currentChart;
        
        // Prepare data for scatterplot - fix the duplicate balance score issue
        const xData = features.map(f => f.properties[xField]).filter(v => v != null);
        
        // For Y-axis, use different metrics based on X-axis selection
        let yField, yData;
        if (xField === 'balance_score') {
            // If X is balance score, show total greenery on Y
            yField = 'total_greenery';
            yData = features.map(f => f.properties.total_greenery).filter(v => v != null);
        } else if (xField === 'welfare_recipients' || xField === 'population_total') {
            // If X is CBS data, show total greenery on Y
            yField = 'total_greenery';
            yData = features.map(f => f.properties.total_greenery).filter(v => v != null);
        } else {
            // Default: show balance score on Y
            yField = 'balance_score';
            yData = features.map(f => f.properties.balance_score).filter(v => v != null);
        }

        const colors = features.map(f => f.properties.color);
        const pcodes = features.map(f => f.properties.PC4);

        const trace = {
            x: xData,
            y: yData,
            mode: 'markers',
            type: 'scatter',
            marker: {
                color: colors,
                size: 6,
                opacity: 0.7,
                line: {
                    color: 'white',
                    width: 0.5
                }
            },
            text: pcodes,
            hovertemplate: `<b>PC4: %{text}</b><br>${this.formatFieldName(xField)}: %{x}<br>${this.formatFieldName(yField)}: %{y}<extra></extra>`
        };

        const layout = {
            title: {
                text: `${this.formatFieldName(xField)} vs ${this.formatFieldName(yField)}`,
                font: { size: 14 }
            },
            xaxis: { 
                title: this.formatFieldName(xField),
                gridcolor: '#f0f0f0'
            },
            yaxis: { 
                title: this.formatFieldName(yField),
                gridcolor: '#f0f0f0'
            },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            margin: { t: 40, r: 20, b: 40, l: 60 },
            font: { family: 'Segoe UI, sans-serif', size: 11 }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot('scatterplot', [trace], layout, config);
    }

    formatFieldName(field) {
        const fieldNames = {
            'total_greenery': 'Total Greenery (%)',
            'balance_score': 'Balance Score (0-100)',
            'trees_pct': 'Trees (%)',
            'bushes_pct': 'Bushes (%)',
            'grass_pct': 'Grass (%)',
            'welfare_recipients': 'Welfare Recipients',
            'population_total': 'Population Total'
        };
        return fieldNames[field] || field.replace(/_/g, ' ');
    }

    updateDetailsPanel(properties) {
        const panel = document.querySelector('.details-content');
        const empty = document.querySelector('.details-empty');
        
        empty.style.display = 'none';
        panel.style.display = 'block';
        panel.classList.add('active');

        panel.innerHTML = `
            <div class="postcode-header">
                <h3>Postcode ${properties.PC4}</h3>
                <div class="postcode-subtitle">Detailed Green Space Analysis</div>
            </div>

            <div class="detail-section">
                <h4>Green Space Composition</h4>
                <div class="greenery-bars">
                    <div class="greenery-bar">
                        <span class="bar-label">Trees</span>
                        <div class="bar-container">
                            <div class="bar-fill trees" style="width: ${properties.trees_pct}%"></div>
                        </div>
                        <span class="bar-value">${properties.trees_pct.toFixed(1)}%</span>
                    </div>
                    <div class="greenery-bar">
                        <span class="bar-label">Bushes</span>
                        <div class="bar-container">
                            <div class="bar-fill bushes" style="width: ${properties.bushes_pct}%"></div>
                        </div>
                        <span class="bar-value">${properties.bushes_pct.toFixed(1)}%</span>
                    </div>
                    <div class="greenery-bar">
                        <span class="bar-label">Grass</span>
                        <div class="bar-container">
                            <div class="bar-fill grass" style="width: ${properties.grass_pct}%"></div>
                        </div>
                        <span class="bar-value">${properties.grass_pct.toFixed(1)}%</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Calculated Metrics</h4>
                <div class="stat-item">
                    <span class="stat-label">Total Greenery</span>
                    <span class="stat-value">${properties.total_greenery.toFixed(1)}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Balance Score</span>
                    <span class="stat-value">${properties.balance_score.toFixed(2)} ${properties.balance_score > 50 ? '(balanced)' : properties.balance_score > 30 ? '(moderate)' : '(dominated)'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Trivariate Color</span>
                    <span class="stat-value">
                        <div style="display: inline-block; width: 20px; height: 20px; background: ${properties.color}; border: 1px solid #ccc; vertical-align: middle;"></div>
                        ${properties.color}
                    </span>
                </div>
            </div>

            ${this.generateCBSSection(properties)}
        `;
    }

    generateCBSSection(properties) {
        // Find CBS data columns
        const cbsData = Object.entries(properties).filter(([key, value]) => 
            !['PC4', 'trees_pct', 'bushes_pct', 'grass_pct', 'total_greenery', 'balance_score', 'color'].includes(key) 
            && value != null
        );

        if (cbsData.length === 0) return '';

        return `
            <div class="detail-section">
                <h4>CBS Socio-Economic Data</h4>
                ${cbsData.map(([key, value]) => `
                    <div class="stat-item">
                        <span class="stat-label">${key.replace(/_/g, ' ')}</span>
                        <span class="stat-value">${typeof value === 'number' ? value.toLocaleString() : value}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    clearDetailsPanel() {
        const panel = document.querySelector('.details-content');
        const empty = document.querySelector('.details-empty');
        
        panel.style.display = 'none';
        panel.classList.remove('active');
        empty.style.display = 'block';
    }

    showError(message) {
        console.error('Error:', message);
        // You could implement a toast notification or error panel here
        alert(`Error: ${message}`);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GreenSpaceDashboard();
}); 