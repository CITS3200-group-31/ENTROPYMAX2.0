"""
GPS CSV validator strictly following the sample_coordinates.csv format.

Expected header (exact, case-sensitive):
  Sample Name,Latitude,Longitude

Returns (valid: bool, error_message: str)
"""
from pathlib import Path
from typing import Tuple, List
import pandas as pd


def _first_n_rows(indexes, n=5) -> List[int]:
    return [int(i) + 2 for i in list(indexes)[:n]]  # +2 => header is row 1


def validate_gps_csv(file_path: str) -> Tuple[bool, str]:
    try:
        p = Path(file_path)
        if not p.exists():
            return False, f"File not found: {file_path}"
        if p.suffix.lower() != ".csv":
            return False, "File must have .csv extension"

        # Read as raw and trim header whitespace; drop unnamed/blank columns entirely
        df = pd.read_csv(file_path, low_memory=False)
        raw_cols = list(df.columns)
        keep_mask = [bool(str(c).strip()) and not str(c).lower().startswith("unnamed") for c in raw_cols]
        df = df.loc[:, [c for c, k in zip(raw_cols, keep_mask) if k]]

        # Must be exactly three columns in strict order (case-sensitive)
        expected_cols = ["Sample Name", "Latitude", "Longitude"]
        found_cols = [str(c).strip() for c in df.columns]
        if len(found_cols) != 3:
            return False, (
                "GPS file must have exactly 3 columns in order: "
                f"{expected_cols}. Found {len(found_cols)} column(s): {found_cols}"
            )
        if found_cols != expected_cols:
            hint = ""
            if found_cols and found_cols[0] == "Sample":
                hint = " Hint: first column must be 'Sample Name', not 'Sample'."
            return False, (
                "Header mismatch (case-sensitive). Expected "
                f"{expected_cols}, found {found_cols}.{hint}"
            )

        # No empty sample names
        samples = df["Sample Name"].astype(str).str.strip()
        if samples.eq("").any():
            rows = _first_n_rows(samples[samples.eq("")].index)
            return False, f"Empty 'Sample Name' at rows: {rows} (showing up to 5)."


        # Latitude/Longitude numeric and in range
        for col, min_v, max_v in [("Latitude", -90, 90), ("Longitude", -180, 180)]:
            raw_series = df[col]
            numeric = pd.to_numeric(raw_series, errors="coerce")
            non_numeric_mask = numeric.isna()
            if non_numeric_mask.any():
                rows = _first_n_rows(non_numeric_mask[non_numeric_mask].index)
                return False, f"Column '{col}' has non-numeric or missing values at rows: {rows} (showing up to 5)."
            out_of_range = ~numeric.between(min_v, max_v)
            if out_of_range.any():
                rows = _first_n_rows(out_of_range[out_of_range].index)
                return False, f"{col} out of range [{min_v}, {max_v}] at rows: {rows} (showing up to 5)."

        # At least one data row present
        if df.shape[0] < 1:
            return False, "No data rows found"

        return True, ""

    except Exception as e:
        return False, f"Error reading file: {str(e)}"
