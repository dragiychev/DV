#!/usr/bin/env python3
"""Add trivariate colors and finalize the advanced green space dataset.

Reads the CBS-merged data, adds RGB colors for trivariate choropleth, 
and exports ``data/processed_green_space_advanced.geojson``.
"""
from pathlib import Path
import pandas as pd
import geopandas as gpd
import importlib, fiona

# Ensure fiona.path exists for geopandas 0.14 + Fiona 1.9 edge cases
if not hasattr(fiona, "path"):
    try:
        fiona.path = importlib.import_module("fiona.path")  # type: ignore
    except ModuleNotFoundError:
        pass

INPUT_FILE = Path("data/green_space_with_cbs_fixed.geojson")
OUTPUT_FILE = Path("data/processed_green_space_advanced.geojson")

if not INPUT_FILE.exists():
    raise SystemExit(f"Missing input {INPUT_FILE}. Run previous scripts first.")

print("Loading merged dataset...")
gdf = gpd.read_file(INPUT_FILE)

print(f"Input columns: {list(gdf.columns)}")
print(f"Input shape: {gdf.shape}")

def calculate_color(trees: float, bushes: float, grass: float) -> str:
    """
    Calculate RGB hex color for trivariate choropleth based on Trees/Bushes/Grass percentages.
    
    Trees → Red channel
    Bushes → Green channel  
    Grass → Blue channel
    
    Returns hex color like '#FF8040'
    """
    # Normalize to 0-255 range (assuming input percentages are 0-100)
    r = max(0, min(255, int(trees * 2.55)))  # Trees → Red
    g = max(0, min(255, int(bushes * 2.55))) # Bushes → Green
    b = max(0, min(255, int(grass * 2.55)))  # Grass → Blue
    
    return f"#{r:02X}{g:02X}{b:02X}"

print("Calculating trivariate colors...")
# Add color column
gdf["color"] = gdf.apply(
    lambda row: calculate_color(
        row.get("trees_pct", 0), 
        row.get("bushes_pct", 0), 
        row.get("grass_pct", 0)
    ), 
    axis=1
)

print("Dataset summary:")
print(f"Total postcodes: {len(gdf):,}")
print(f"Columns: {list(gdf.columns)}")

# Show some stats
if "total_greenery" in gdf.columns:
    print(f"Total greenery range: {gdf['total_greenery'].min():.1f}% - {gdf['total_greenery'].max():.1f}%")
if "balance_score" in gdf.columns:
    print(f"Balance score range: {gdf['balance_score'].min():.2f} - {gdf['balance_score'].max():.2f}")

# Show sample with CBS data
cbs_cols = [col for col in gdf.columns if col not in ['PC4', 'trees_pct', 'bushes_pct', 'grass_pct', 'geometry', 'color', 'total_greenery', 'balance_score']]
if cbs_cols:
    print(f"CBS columns available: {cbs_cols}")
    print("Sample data with CBS info:")
    sample_data = gdf[gdf[cbs_cols[0]].notna()].head(3)
    for _, row in sample_data.iterrows():
        print(f"  PC4 {row['PC4']}: Trees={row.get('trees_pct', 0):.1f}%, CBS={row[cbs_cols[0]]}")

print("Writing final dataset...")
gdf.to_file(OUTPUT_FILE, driver="GeoJSON")
print(f"✅ Complete dataset → {OUTPUT_FILE}")
print("\n🎯 Ready for Phase 2: Flask Backend!") 