import os
import sys
import pandas as pd


def _normalize_sample_column(df: pd.DataFrame, src_colnames=("Sample", "Sample Name")) -> pd.DataFrame:
    cols_lower = {c.lower().strip(): c for c in df.columns}
    # Prefer 'sample' if present; fallback to 'sample name'
    if "sample" in cols_lower:
        sc = cols_lower["sample"]
        if sc != "Sample":
            df = df.rename(columns={sc: "Sample"})
    elif "sample name" in cols_lower:
        df = df.rename(columns={cols_lower["sample name"]: "Sample"})
    return df


def append_lat_lon_and_write_parquet(algo_csv_path: str, gps_csv_path: str, output_parquet_path: str) -> None:
    # Read algorithm output (CSV)
    out_df = pd.read_csv(algo_csv_path)
    out_df = _normalize_sample_column(out_df)
    if "Sample" not in out_df.columns:
        raise ValueError("Algorithm output must contain 'Sample' column")

    # Read GPS CSV and normalize sample column
    gps_df = pd.read_csv(gps_csv_path)
    gps_df = _normalize_sample_column(gps_df)
    # Normalize GPS lat/lon headers
    rename_map = {}
    for c in gps_df.columns:
        lc = c.lower().strip()
        if lc == "latitude":
            rename_map[c] = "latitude"
        if lc == "longitude":
            rename_map[c] = "longitude"
    if rename_map:
        gps_df = gps_df.rename(columns=rename_map)
    required = {"Sample", "latitude", "longitude"}
    if not required.issubset(set(gps_df.columns)):
        raise ValueError(f"GPS CSV must have columns Sample/Latitude/Longitude (case-insensitive). Got: {list(gps_df.columns)}")

    # Prepare join keys
    out_df["Sample"] = out_df["Sample"].astype(str).str.strip()
    gps_df["Sample"] = gps_df["Sample"].astype(str).str.strip()

    # Merge; preserve original algo columns order, append lat/long at end
    merged = out_df.merge(gps_df[["Sample", "latitude", "longitude"]], on="Sample", how="left")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)
    merged.to_parquet(output_parquet_path, index=False)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 postprocess_output.py <algo_output.csv> <gps.csv> <output.parquet>")
        sys.exit(1)
    try:
        append_lat_lon_and_write_parquet(sys.argv[1], sys.argv[2], sys.argv[3])
        print(f"Wrote {sys.argv[3]}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)


