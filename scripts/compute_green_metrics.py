#!/usr/bin/env python3
"""Compute advanced greenery metrics (balance score & total).

Run after ``data_preparation.py``. Produces ``data/green_space_with_metrics.geojson``.
"""
from pathlib import Path
import numpy as np
import geopandas as gpd
import importlib, fiona

# Ensure fiona.path exists for geopandas 0.14 + Fiona 1.9 edge cases
if not hasattr(fiona, "path"):
    try:
        fiona.path = importlib.import_module("fiona.path")  # type: ignore
    except ModuleNotFoundError:
        pass

INPUT_FILE = Path("data/merged_green_space_base.geojson")
OUTPUT_FILE = Path("data/green_space_with_metrics.geojson")

if not INPUT_FILE.exists():
    raise SystemExit(f"Missing input {INPUT_FILE}. Run scripts/data_preparation.py first.")

gdf = gpd.read_file(INPUT_FILE)

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def calculate_balance_score(trees: float, bushes: float, grass: float) -> float:
    """Return std-dev of the three percentages (lower = balanced)."""
    return float(np.std([trees, bushes, grass]))

print("Calculating metrics …")

gdf["total_greenery"] = gdf[["trees_pct", "bushes_pct", "grass_pct"]].sum(axis=1)

gdf["balance_score"] = gdf.apply(
    lambda row: calculate_balance_score(row["trees_pct"], row["bushes_pct"], row["grass_pct"]), axis=1
)

print("Writing output …")
gdf.to_file(OUTPUT_FILE, driver="GeoJSON")
print(f"Done → {OUTPUT_FILE}") 