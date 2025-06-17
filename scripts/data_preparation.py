#!/usr/bin/env python3
"""Prepare base dataset: merge Dutch PC4 geometries with green-space percentages.

Usage::
    python scripts/data_preparation.py

Outputs ``data/merged_green_space_base.geojson``
"""
from pathlib import Path
import requests
import pandas as pd
import geopandas as gpd
import importlib, fiona

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Download PC4 geometries from Opendatasoft (if missing)
# ---------------------------------------------------------------------------
PC4_URL = (
    "https://public.opendatasoft.com/explore/dataset/georef-netherlands-postcode-pc4/download/"
    "?format=geojson&timezone=Europe/Amsterdam&lang=en"
)
PC4_FILE = DATA_DIR / "pc4_nl.geojson"

if not PC4_FILE.exists():
    print("Downloading Dutch PC4 geometries …")
    resp = requests.get(PC4_URL, timeout=60)
    resp.raise_for_status()
    PC4_FILE.write_bytes(resp.content)
    print(f"Saved {PC4_FILE}")
else:
    print(f"Using cached {PC4_FILE}")

# ---------------------------------------------------------------------------
# Load geometries and attribute data
# ---------------------------------------------------------------------------
print("Loading geometries…")

# Ensure fiona.path is available for geopandas (work-around for some Fiona builds)
if not hasattr(fiona, "path"):
    try:
        fiona.path = importlib.import_module("fiona.path")  # type: ignore
    except ModuleNotFoundError:
        pass  # will raise later if geopandas really requires it

# Read GeoJSON
gdf_raw = gpd.read_file(PC4_FILE, low_memory=False)

# Determine the column that holds the four-digit postcode code.
postcode_col = None
for cand in ("postcode", "pc4_code", "pc4", "code", "pc4_cd"):
    if cand in gdf_raw.columns:
        postcode_col = cand
        break
if postcode_col is None:
    raise KeyError("Could not find a postcode column in the PC4 GeoJSON. Available columns: " + ", ".join(gdf_raw.columns))

# Keep only code + geometry and standardise to 'PC4'
gdf_pc4 = gdf_raw[[postcode_col, "geometry"]].rename(columns={postcode_col: "PC4"})
# Ensure consistent string dtype
gdf_pc4["PC4"] = gdf_pc4["PC4"].astype(str)

# Load percentages CSV (European decimal comma, semicolon separator)
CSV_FILE = Path("PC4_TreesBushesGrass.csv")
print("Loading green-space CSV…")
df_green = (
    pd.read_csv(CSV_FILE, sep=";", decimal=",")
    .rename(
        columns={
            "Postcode": "PC4",
            "PercentageTrees": "trees_pct",
            "PercentageBushes": "bushes_pct",
            "PercentageGrass": "grass_pct",
        }
    )
)

# Ensure PC4 is string formatted without decimals
for col in ("PC4",):
    df_green[col] = df_green[col].astype(str)

gdf = gdf_pc4.merge(df_green, on="PC4", how="inner")
print(f"Merged records: {len(gdf):,}")

OUT_FILE = DATA_DIR / "merged_green_space_base.geojson"
print(f"Writing {OUT_FILE} …")
gdf.to_file(OUT_FILE, driver="GeoJSON")
print("Done.") 