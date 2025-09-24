import os
import sys
import pandas as pd

from validate_csv_raw import validate_csv_structure
from validate_csv_gps import validate_csv_gps_structure
from convert_csv_to_parquet import convert_csv_to_parquet
from run_combine import combine_parquet_files


def _ensure_csv(path: str) -> None:
    if not path.lower().endswith(".csv"):
        raise ValueError(f"Expected a .csv file: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(path)


def _derived_parquet_path(csv_path: str) -> str:
    return os.path.splitext(csv_path)[0] + ".parquet"


def _cursory_schema_check_after_convert(parquet_path: str, required_cols: list[str]) -> None:
    df = pd.read_parquet(parquet_path)
    cols = [c.strip().lower() for c in df.columns]
    # Special-case: accept 'sample' or 'sample name' for the PK in raw
    normalized_required = []
    for c in required_cols:
        if c == "sample":
            if ("sample" in cols) or ("sample name" in cols):
                continue
        normalized_required.append(c)
    missing = [c for c in normalized_required if c not in cols]
    if missing:
        raise ValueError(f"Converted parquet missing columns: {missing}; has: {cols}")


def build_merged_parquet(raw_csv: str, gps_csv: str, merged_parquet_out: str) -> None:
    # 1) Validate CSVs
    _ensure_csv(raw_csv)
    _ensure_csv(gps_csv)
    validate_csv_structure(raw_csv)
    validate_csv_gps_structure(gps_csv)

    # 2) Convert both to Parquet (lowercased headers)
    raw_parquet = _derived_parquet_path(raw_csv)
    gps_parquet = _derived_parquet_path(gps_csv)
    convert_csv_to_parquet(raw_csv, raw_parquet)
    convert_csv_to_parquet(gps_csv, gps_parquet)

    # 3) Cursory post-conversion checks to catch header misalignment
    #    Expect raw to contain at least 'sample' (lowercased from 'Sample Name')
    #    Expect gps to contain 'sample','latitude','longitude'
    _cursory_schema_check_after_convert(raw_parquet, ["sample"])
    _cursory_schema_check_after_convert(gps_parquet, ["sample", "latitude", "longitude"])

    # 4) Merge on 'sample' and write merged parquet
    combine_parquet_files(raw_parquet, gps_parquet, merged_parquet_out)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 io_pipeline.py <raw.csv> <gps.csv> <merged.parquet>")
        sys.exit(1)
    try:
        build_merged_parquet(sys.argv[1], sys.argv[2], sys.argv[3])
        print(f"Merged parquet written to: {sys.argv[3]}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)


