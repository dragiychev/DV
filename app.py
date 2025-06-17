#!/usr/bin/env python3
"""Flask backend for the Advanced Dutch Green Space Dashboard.

Serves the enriched green space data with trivariate colors, balance scores,
and socio-economic data for the multi-view dashboard.
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import geopandas as gpd
import json
from pathlib import Path
import importlib, fiona

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure fiona.path exists for geopandas 0.14 + Fiona 1.9 edge cases
if not hasattr(fiona, "path"):
    try:
        fiona.path = importlib.import_module("fiona.path")  # type: ignore
    except ModuleNotFoundError:
        pass

# Load the processed data on startup
DATA_FILE = Path("data/processed_green_space_advanced.geojson")

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Missing data file: {DATA_FILE}")

print("Loading advanced green space dataset...")
gdf = gpd.read_file(DATA_FILE)
print(f"Loaded {len(gdf):,} postcode areas with {len(gdf.columns)} attributes")

@app.route('/')
def home():
    """Serve the dashboard homepage."""
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS)."""
    return send_from_directory('static', filename)

@app.route('/api/green_space_advanced')
def get_green_space_data():
    """
    Return the complete green space dataset as GeoJSON.
    
    Includes:
    - PC4 geometries
    - Trees/Bushes/Grass percentages  
    - Trivariate colors
    - Balance scores
    - Total greenery
    - CBS socio-economic data
    """
    try:
        # Convert to GeoJSON format
        geojson_data = json.loads(gdf.to_json())
        
        # Add metadata
        response = {
            "type": "FeatureCollection",
            "metadata": {
                "total_features": len(gdf),
                "data_source": "CBS Netherlands + Dutch Green Space Analysis",
                "date_generated": "2025",
                "attributes": {
                    "PC4": "4-digit postcode",
                    "trees_pct": "Trees percentage (0-100)",
                    "bushes_pct": "Bushes percentage (0-100)", 
                    "grass_pct": "Grass percentage (0-100)",
                    "total_greenery": "Sum of all green percentages",
                    "balance_score": "Standard deviation of T/B/G (lower = more balanced)",
                    "color": "Trivariate RGB hex color",
                    "cbs_data": "Socio-economic data from CBS"
                }
            },
            "features": geojson_data["features"]
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": f"Failed to load data: {str(e)}"}), 500

@app.route('/api/statistics')
def get_statistics():
    """
    Return summary statistics for the dashboard.
    """
    try:
        # Calculate various statistics
        stats = {
            "total_postcodes": int(len(gdf)),
            "greenery_stats": {
                "trees": {
                    "min": float(gdf["trees_pct"].min()),
                    "max": float(gdf["trees_pct"].max()),
                    "mean": float(gdf["trees_pct"].mean())
                },
                "bushes": {
                    "min": float(gdf["bushes_pct"].min()),
                    "max": float(gdf["bushes_pct"].max()),
                    "mean": float(gdf["bushes_pct"].mean())
                },
                "grass": {
                    "min": float(gdf["grass_pct"].min()),
                    "max": float(gdf["grass_pct"].max()),
                    "mean": float(gdf["grass_pct"].mean())
                }
            },
            "total_greenery": {
                "min": float(gdf["total_greenery"].min()),
                "max": float(gdf["total_greenery"].max()),
                "mean": float(gdf["total_greenery"].mean())
            },
            "balance_score": {
                "min": float(gdf["balance_score"].min()),
                "max": float(gdf["balance_score"].max()),
                "mean": float(gdf["balance_score"].mean())
            }
        }
        
        # Add CBS data stats if available
        cbs_cols = [col for col in gdf.columns if col not in ['PC4', 'trees_pct', 'bushes_pct', 'grass_pct', 'geometry', 'color', 'total_greenery', 'balance_score']]
        if cbs_cols:
            stats["cbs_data"] = {}
            for col in cbs_cols:
                non_null_data = gdf[col].dropna()
                if len(non_null_data) > 0:
                    stats["cbs_data"][col] = {
                        "available_records": int(len(non_null_data)),
                        "min": float(non_null_data.min()) if non_null_data.dtype in ['int64', 'float64'] else None,
                        "max": float(non_null_data.max()) if non_null_data.dtype in ['int64', 'float64'] else None,
                        "mean": float(non_null_data.mean()) if non_null_data.dtype in ['int64', 'float64'] else None
                    }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": f"Failed to calculate statistics: {str(e)}"}), 500

@app.route('/api/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "data_loaded": True,
        "records": len(gdf)
    })

if __name__ == '__main__':
    print("\n🚀 Starting Advanced Green Space Dashboard Server...")
    print(f"📊 Data: {len(gdf):,} postcode areas loaded")
    print("🌐 Server: http://localhost:5010")
    print("📡 API: http://localhost:5010/api/green_space_advanced")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5010) 