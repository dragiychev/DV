# 🌳 Advanced Multi-View Dashboard for Dutch Green Space Analysis

A comprehensive data visualization dashboard analyzing green space distribution across the Netherlands using trivariate choropleth mapping, interactive charts, and CBS socio-economic correlations.

![Dashboard Preview](https://img.shields.io/badge/Status-Complete-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0+-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Project Overview

This project creates an **advanced, multi-view dashboard** that combines:

- **Trivariate Choropleth Mapping** with Trees→Red, Bushes→Green, Grass→Blue color encoding
- **3D Extrusion Heights** based on total greenery percentages  
- **Interactive Scatterplot Analysis** showing correlations between green space and socio-economic metrics
- **CBS Socio-Economic Integration** for demographic and welfare analysis
- **Linked Multi-View Interface** with coordinated highlighting and selection

### 📊 Key Metrics Analyzed

- **Green Space Composition**: Trees, Bushes, Grass percentages per postcode
- **Balance Score**: Diversity index (0-100) measuring vegetation balance (higher = more balanced)
- **Total Greenery**: Sum of all green space percentages
- **CBS Demographics**: Population totals and welfare recipient statistics

### 🎯 **CBS Welfare Analysis**
The dashboard includes comprehensive socio-economic analysis using CBS (Statistics Netherlands) data:
- **Welfare Recipients vs Green Space**: Analyze correlation between social welfare and environmental access
- **Population Density vs Greenery**: Urban planning insights for green space distribution
- **Environmental Justice**: Identify areas with low green space and high welfare dependency

## 🏗️ Architecture

```
📦 Dutch Green Space Dashboard
├── 🗃️ data/                          # Processed datasets
│   ├── pc4_2024_v1.xlsx             # CBS socio-economic data
│   └── processed_green_space_advanced.geojson  # Final dataset (4,067 postcodes)
├── 🐍 scripts/                       # Data processing pipeline
│   ├── data_preparation.py           # Step 1: PC4 boundaries + green space merge
│   ├── compute_green_metrics.py      # Step 2: Balance score & total greenery
│   ├── merge_cbs_data.py             # Step 3: CBS demographic integration
│   └── finalize_dataset.py           # Step 4: Trivariate color generation
├── 🌐 Backend
│   └── app.py                        # Flask API server (port 5010)
├── 🎨 Frontend
│   ├── index.html                    # Main dashboard interface
│   └── static/
│       ├── style.css                 # Modern CSS Grid layout
│       └── script.js                 # Interactive application logic
├── 🔐 Configuration
│   ├── config.example.js             # API key template
│   └── config.js                     # Your API keys (gitignored)
├── 📋 Management
│   ├── requirements.txt              # Python dependencies
│   ├── .gitignore                    # Git ignore rules
│   └── README.md                     # This file
└── 📁 Input Data
    └── PC4_TreesBushesGrass.csv      # Your original green space data
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/dutch-green-space-dashboard.git
cd dutch-green-space-dashboard

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example config file
cp config.example.js config.js

# Edit config.js and add your Mapbox token
# Get free token at: https://account.mapbox.com/access-tokens/
```

### 3. Data Processing Pipeline

**⚠️ Important**: The final processed dataset (`data/processed_green_space_advanced.geojson`) is not included in this repository due to GitHub's 100MB file size limit. You must run the data processing pipeline to generate it locally.

Run the complete data preparation pipeline:

```bash
# Step 1: Download PC4 boundaries and merge with green space data
python scripts/data_preparation.py

# Step 2: Calculate balance scores and total greenery metrics
python scripts/compute_green_metrics.py

# Step 3: Integrate CBS socio-economic data
python scripts/merge_cbs_data.py

# Step 4: Generate trivariate colors and finalize dataset
python scripts/finalize_dataset.py
```

**Expected Output:**
- ✅ `data/processed_green_space_advanced.geojson` (4,067 postcode areas, ~179MB)
- ✅ Complete dataset with trivariate colors, balance scores, and CBS demographics

### 4. Launch Dashboard

```bash
# Start Flask server
python app.py

# Open browser to: http://localhost:5010
```

## 🎨 Dashboard Features

### 🗺️ **Interactive Map**
- **Trivariate Choropleth**: Trees→Red, Bushes→Green, Grass→Blue color mixing
- **3D Mode**: Extrusion heights represent total greenery percentages
- **Hover Effects**: Orange highlighting with smooth transitions
- **Click Selection**: Detailed postcode analysis in sidebar

### 📈 **Analysis Panel** 
**NEW: CBS Socio-Economic Analysis**
- **Welfare Recipients vs Total Greenery**: Environmental justice analysis
- **Population vs Total Greenery**: Urban density and green space correlation
- **Balance Score vs Total Greenery**: Vegetation diversity analysis
- **Trees % vs Balance Score**: Species composition insights
- **Color-Coded Points**: Each point uses the trivariate color from the map

### 🔍 **Details Panel**
- **Postcode Profiles**: Complete green space breakdown
- **Visual Bar Charts**: Animated Trees/Bushes/Grass composition
- **Balance Score**: Improved interpretation (50+ = balanced, 30-50 = moderate, <30 = dominated)
- **CBS Integration**: Population and welfare recipient statistics

### 📊 **Statistics Dashboard**
- **Dataset Overview**: 4,067 postcodes with complete metadata
- **Green Space Distribution**: Trees (32.6%), Bushes (8.7%), Grass (47.6%) averages
- **Balance Score Range**: 0-70 (mean: 41.4) - higher scores indicate more balanced vegetation
- **CBS Coverage**: 4,053 postcodes with population data, 3,796 with welfare data

## 🧮 Advanced Analytics

### Improved Balance Score Calculation
```python
def calculate_improved_balance_score(trees, bushes, grass):
    """
    Returns diversity index (0-100) based on coefficient of variation.
    - High score (50+): Balanced vegetation mix
    - Medium score (30-50): Moderate balance  
    - Low score (<30): Dominated by single type
    """
    total = trees + bushes + grass
    props = np.array([trees, bushes, grass]) / total
    cv = np.std(props) / np.mean(props)
    return max(0, 100 - (cv * 100))
```

### Trivariate Color Encoding
```python
def calculate_color(trees, bushes, grass):
    """
    RGB channels mapped to green space types:
    - Red channel ← Trees percentage (0-100 → 0-255)
    - Green channel ← Bushes percentage (0-100 → 0-255)
    - Blue channel ← Grass percentage (0-100 → 0-255)
    """
    r = max(0, min(255, int(trees * 2.55)))
    g = max(0, min(255, int(bushes * 2.55))) 
    b = max(0, min(255, int(grass * 2.55)))
    return f"#{r:02X}{g:02X}{b:02X}"
```

## 🔗 API Endpoints

### `GET /api/green_space_advanced`
Returns complete GeoJSON dataset with:
- PC4 postcode geometries
- Trees/Bushes/Grass percentages
- Balance scores and total greenery metrics
- Trivariate hex colors for visualization
- CBS population and welfare recipient data

### `GET /api/statistics`
Returns comprehensive statistics:
- Dataset overview (4,067 total postcodes)
- Green space distribution (min/max/mean for each type)
- Balance score ranges (0-70 scale)
- CBS data coverage (population: 4,053 records, welfare: 3,796 records)

### `GET /api/health`
Simple health check endpoint for monitoring server status.

## 🎯 Technical Highlights

### **Advanced Data Integration**
- **Automated PC4 Download**: Fetches Dutch postcode boundaries from OpenDataSoft API
- **CBS Excel Processing**: Handles complex multi-row headers and data type conversion
- **Robust Data Cleaning**: Removes CBS sentinel values (-99997) and handles missing data
- **Column Standardization**: Consistent naming and type conversion across datasets

### **Sophisticated Visualization**
- **Trivariate Color Mixing**: True RGB encoding of three-dimensional vegetation data
- **Dynamic Y-axis Selection**: Smart chart logic prevents duplicate variable plotting
- **3D Extrusion Mapping**: Height-based encoding for total greenery visualization
- **Linked Multi-View Interface**: Map selection synchronizes with charts and details

### **Performance & Scalability**
- **Backend Caching**: GeoJSON dataset loaded once at startup for fast responses
- **Efficient Frontend**: Mapbox GL JS hardware acceleration with minimal dependencies
- **Responsive Design**: CSS Grid layout adapts seamlessly to different screen sizes
- **API-First Architecture**: Clean separation between data processing and visualization

## 📋 Development Status

**✅ ALL FEATURES COMPLETE:**

- [x] **Data Processing Pipeline**: 4-stage automated processing with CBS integration
- [x] **Flask REST API**: CORS-enabled server with comprehensive endpoints (port 5010)
- [x] **Interactive Dashboard**: Modern tabbed interface with real-time updates
- [x] **Trivariate Choropleth**: Advanced color encoding for 3-variable visualization
- [x] **3D Extrusion Mode**: Height-based representation of total greenery
- [x] **CBS Socio-Economic Analysis**: Welfare recipients and population correlation charts
- [x] **Improved Balance Score**: 0-100 scale with proper diversity interpretation
- [x] **Responsive Details Panel**: Complete postcode profiles with animated charts

## 🛠️ Development Setup

### For Contributors

```bash
# Clone the repository
git clone https://github.com/yourusername/dutch-green-space-dashboard.git
cd dutch-green-space-dashboard

# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Environment Variables

Create a `config.js` file with your API keys:
```javascript
const CONFIG_SECRETS = {
    mapbox: {
        accessToken: 'your-mapbox-token-here'
    }
};
window.CONFIG_SECRETS = CONFIG_SECRETS;
```

## 🔧 Dependencies

### Python Backend
- `pandas==2.2.2` - Data manipulation and analysis
- `geopandas==0.14.3` - Geospatial data operations  
- `flask==3.0.2` - Web application framework
- `flask-cors==4.0.0` - Cross-origin resource sharing
- `openpyxl==3.1.2` - Excel file reading for CBS data

### Frontend Libraries
- **Mapbox GL JS v3.0.1** - Interactive maps with 3D rendering capabilities
- **Plotly.js v2.26.0** - Statistical charts and data visualization
- **Modern CSS Grid** - Responsive layout without external frameworks

## 🎓 Educational Value

This project demonstrates advanced concepts in:

1. **Multi-Dimensional Data Visualization**: Trivariate choropleth mapping
2. **Full-Stack Geospatial Development**: Python backend with JavaScript frontend
3. **Statistical Analysis**: Balance score calculation and correlation analysis
4. **Data Integration**: Combining multiple government datasets (CBS + OpenDataSoft)
5. **User Experience Design**: Intuitive multi-view interface with linked interactions
6. **Environmental Data Science**: Green space analysis for urban planning

## 📈 Potential Extensions

- **Temporal Analysis**: Historical green space changes over multiple years
- **Machine Learning**: Clustering analysis for green space pattern recognition
- **Environmental Correlation**: Integration with air quality and urban heat data
- **Public Health Analysis**: Green space access vs health outcome correlations
- **Predictive Modeling**: Optimal green space distribution for urban planning

## 🚀 Deployment

### Local Development
```bash
python app.py  # Starts server on http://localhost:5010
```

### Production Deployment
For production deployment, consider:
- Using Gunicorn or uWSGI for the Flask application
- Setting up reverse proxy with Nginx
- Implementing proper logging and error handling
- Adding rate limiting for API endpoints

## 📄 License

MIT License - Feel free to use this project for educational, research, or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions about the implementation or to report issues:
- Review the code documentation in source files
- Check the data processing pipeline in the `scripts/` directory
- Examine the API endpoints in `app.py`
- Study the frontend interaction logic in `static/script.js`

---

**🌱 Built with passion for environmental data visualization and urban sustainability analysis**

*This dashboard provides actionable insights for urban planners, environmental researchers, and policy makers working on green space equity and environmental justice initiatives.* 