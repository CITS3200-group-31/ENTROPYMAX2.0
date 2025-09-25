import os
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def run(in_parquet: str, out_parquet: str, coords_cols=("Latitude", "Longitude")) -> None:
    # Load merged parquet (must contain 'Sample' plus numeric bins, and lat/lon columns)
    table = pq.read_table(in_parquet)
    df = table.to_pandas()

    # Normalize columns
    df.columns = [str(c).strip() for c in df.columns]
    if "Sample" not in df.columns and "Sample Name" in df.columns:
        df = df.rename(columns={"Sample Name": "Sample"})
    df["Sample"] = df["Sample"].astype(str).str.strip()

    # Split coords and numeric bins
    lat_col, lon_col = coords_cols
    if lat_col not in df.columns or lon_col not in df.columns:
        raise RuntimeError(f"Input parquet must include '{lat_col}' and '{lon_col}' columns.")

    # Prefer native Parquet I/O if compiled in: pass EM_INPUT_PARQUET/EM_OUTPUT_PARQUET
    os.makedirs("data/processed", exist_ok=True)
    cmd = f"EM_INPUT_PARQUET={in_parquet} EM_OUTPUT_PARQUET={out_parquet} ./build-make/bin/run_entropymax"
    import subprocess
    proc = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    csv_text = proc.stdout

    # Convert CSV text directly to Parquet
    out_df = pd.read_csv(pd.io.common.StringIO(csv_text))
    out_table = pa.Table.from_pandas(out_df)
    pq.write_table(out_table, out_parquet)
    print(f"Wrote Parquet: {out_parquet}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 run_parquet.py <input_merged.parquet> <output.parquet>")
        sys.exit(2)
    run(sys.argv[1], sys.argv[2])


