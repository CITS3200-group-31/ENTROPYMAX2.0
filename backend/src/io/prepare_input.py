import os
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from validate_csv_raw import validate_csv_structure
from validate_csv_gps import validate_csv_gps_structure


def prepare(raw_csv_path: str, gps_csv_path: str,
            out_dir: str = "data/processed",
            runner_csv_path: str = None,
            coords_map_csv_path: str = None,
            merged_parquet_path: str = None) -> None:
    os.makedirs(out_dir, exist_ok=True)
    if runner_csv_path is None:
        runner_csv_path = os.path.join(out_dir, "input_for_runner.csv")
    if coords_map_csv_path is None:
        coords_map_csv_path = os.path.join(out_dir, "coords_map.csv")
    if merged_parquet_path is None:
        merged_parquet_path = os.path.join(out_dir, "input_merged.parquet")

    # Validate inputs
    validate_csv_structure(raw_csv_path)
    validate_csv_gps_structure(gps_csv_path)

    # Load CSVs
    raw_df_orig = pd.read_csv(raw_csv_path)
    raw_df = raw_df_orig.copy()
    gps_df = pd.read_csv(gps_csv_path)

    # Clean stray unnamed/empty columns
    raw_df = raw_df.loc[:, ~raw_df.columns.astype(str).str.startswith('Unnamed')]
    raw_df = raw_df.dropna(axis=1, how='all')
    gps_df = gps_df.loc[:, ~gps_df.columns.astype(str).str.startswith('Unnamed')]
    gps_df = gps_df.dropna(axis=1, how='all')

    # Normalize and trim 'Sample' names for reliable joins
    raw_df.columns = [str(c).strip() for c in raw_df.columns]
    gps_df.columns = [str(c).strip() for c in gps_df.columns]
    # Normalize sample column name
    if 'Sample' not in gps_df.columns and 'Sample Name' in gps_df.columns:
        gps_df = gps_df.rename(columns={'Sample Name': 'Sample'})
    raw_df['Sample Name'] = raw_df['Sample Name'].astype(str).str.strip()
    if 'Sample' in gps_df.columns:
        gps_df['Sample'] = gps_df['Sample'].astype(str).str.strip()

    # Merge for Parquet (keep all columns including lat/lon and bins)
    merged_df = pd.merge(
        raw_df.rename(columns={'Sample Name': 'Sample'}),
        gps_df, on='Sample', how='left'
    )

    # Write Parquet merged
    table = pa.Table.from_pandas(merged_df)
    pq.write_table(table, merged_parquet_path)

    # Emit runner CSV as an exact copy of the original input.csv (preserve headers, order, tokens)
    raw_df_orig.to_csv(runner_csv_path, index=False)

    # Emit coords map for runner
    coords_df = gps_df[['Sample', 'Latitude', 'Longitude']].copy()
    coords_df.to_csv(coords_map_csv_path, index=False)

    print(f"Prepared:\n  runner CSV: {runner_csv_path}\n  coords map: {coords_map_csv_path}\n  merged parquet: {merged_parquet_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 prepare_input.py <raw_input_csv> <gps_csv>")
        sys.exit(1)
    prepare(sys.argv[1], sys.argv[2])


