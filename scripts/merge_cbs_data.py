#!/usr/bin/env python3
"""Merge CBS socio-economic data with green space metrics.

Reads the CBS Excel file and merges it with the green space data.
Outputs ``data/green_space_with_cbs.geojson``.
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

INPUT_FILE = Path("data/green_space_with_metrics.geojson")
CBS_FILE = Path("data/pc4_2024_v1.xlsx")
OUTPUT_FILE = Path("data/green_space_with_cbs.geojson")

if not INPUT_FILE.exists():
    raise SystemExit(f"Missing input {INPUT_FILE}. Run previous scripts first.")

if not CBS_FILE.exists():
    raise SystemExit(f"Missing CBS data {CBS_FILE}. Please ensure the file is in the data/ directory.")

print("Loading existing green space data...")
gdf = gpd.read_file(INPUT_FILE)

print("Loading CBS Excel data...")
# Load the Excel file - CBS files typically have metadata in first few rows
try:
    # First, let's peek at the raw structure to find where the real data starts
    df_peek = pd.read_excel(CBS_FILE, sheet_name=0, header=None, nrows=10)
    print("First 10 rows of raw Excel:")
    for i, row in df_peek.iterrows():
        print(f"Row {i}: {row[0]} | {row[1] if len(row) > 1 else ''}")
    
    # Look for a row that contains "PC4" or similar - this is likely the header row
    header_row = None
    
    # Based on the peek, we know row 7 contains "Postcode-4", so let's use that
    try:
        df_test = pd.read_excel(CBS_FILE, sheet_name=0, header=7, nrows=5)
        if len(df_test.columns) > 5 and 'Postcode-4' in str(df_test.columns).replace('Unnamed', ''):
            header_row = 7
            print(f"Using header row 7 based on 'Postcode-4' detection")
    except:
        pass
    
    # Only if row 7 doesn't work, try the general detection
    if header_row is None:
        for i in range(10):
            try:
                df_test = pd.read_excel(CBS_FILE, sheet_name=0, header=i, nrows=1)
                cols_str = " ".join(str(col).lower() for col in df_test.columns)
                # Be more specific - avoid the title row which also contains 'postcode'
                if any(term in cols_str for term in ['postcode-4', 'pc4']) and 'unnamed' not in cols_str:
                    header_row = i
                    print(f"Found header row at index {i}")
                    break
            except:
                continue
    
    if header_row is None:
        # Try common header row positions for CBS files
        for test_row in [3, 4, 5, 6, 8]:
            try:
                df_test = pd.read_excel(CBS_FILE, sheet_name=0, header=test_row, nrows=5)
                if len(df_test.columns) > 5 and not all('Unnamed' in str(col) for col in df_test.columns):
                    header_row = test_row
                    print(f"Using header row {test_row} based on column structure")
                    break
            except:
                continue
    
    if header_row is None:
        header_row = 0
        print("Could not determine header row, using row 0")
    
    # Now read with the correct header row
    df_cbs_raw = pd.read_excel(CBS_FILE, sheet_name=0, header=header_row)
    print(f"CBS data shape: {df_cbs_raw.shape}")
    print(f"CBS columns: {list(df_cbs_raw.columns)}")
    
    # Look for postcode and income/wealth columns
    postcode_cols = [col for col in df_cbs_raw.columns if any(term in str(col).lower() for term in ['pc4', 'postcode', 'code'])]
    income_cols = [col for col in df_cbs_raw.columns if any(term in str(col).lower() for term in ['inkomen', 'income', 'woz', 'waarde', 'vermogen'])]
    
    print(f"Potential postcode columns: {postcode_cols}")
    print(f"Potential income/wealth columns: {income_cols}")
    
    if not postcode_cols:
        raise ValueError("No postcode column found in CBS data")
    
    # Use the first postcode column found
    pc_col = postcode_cols[0]
    
    # Select relevant columns for merge
    keep_cols = [pc_col] + income_cols
    # Also keep any other interesting demographic columns
    demo_cols = [col for col in df_cbs_raw.columns if any(term in str(col).lower() for term in 
                ['bevolking', 'inwoners', 'households', 'huishoudens', 'leeftijd', 'age'])]
    keep_cols.extend(demo_cols)
    
    # Remove duplicates and ensure postcode column is first
    keep_cols = [pc_col] + [col for col in keep_cols[1:] if col != pc_col]
    keep_cols = list(dict.fromkeys(keep_cols))  # Remove duplicates while preserving order
    
    print(f"Keeping columns: {keep_cols}")
    
    # Clean and prepare CBS data
    df_cbs = df_cbs_raw[keep_cols].copy()
    df_cbs = df_cbs.rename(columns={pc_col: "PC4"})
    
    # Clean the PC4 column - remove any non-numeric values
    df_cbs["PC4"] = df_cbs["PC4"].astype(str).str.extract(r'(\d{4})')[0]
    df_cbs = df_cbs.dropna(subset=["PC4"])
    df_cbs = df_cbs[df_cbs["PC4"].str.len() == 4]  # Ensure 4-digit postcodes
    
    print(f"CBS data after cleaning: {df_cbs.shape}")
    print(f"Sample CBS data:")
    print(df_cbs.head())

except Exception as e:
    print(f"Error reading CBS Excel file: {e}")
    print("Please check the file format and try again.")
    raise

print("Merging datasets...")
# Merge with green space data
gdf_merged = gdf.merge(df_cbs, on="PC4", how="left")

print(f"Original green space records: {len(gdf):,}")
print(f"After CBS merge: {len(gdf_merged):,}")
print(f"Records with CBS data: {len(gdf_merged.dropna(subset=df_cbs.columns[1:])):,}")

print("Writing merged data...")
gdf_merged.to_file(OUTPUT_FILE, driver="GeoJSON")
print(f"Done → {OUTPUT_FILE}") 