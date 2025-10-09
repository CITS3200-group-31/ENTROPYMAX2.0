"""
Raw data CSV validator strictly following the sample_input.csv format.

Expected header first column (exact, case-sensitive):
  Sample Name
Remaining header columns must be numeric grain-size bins (floats). Order is not enforced.

Returns (valid: bool, error_message: str)
"""
from pathlib import Path
from typing import Tuple, List
import pandas as pd
import numpy as np


def _first_n_rows(indexes, n=5) -> List[int]:
    return [int(i) + 2 for i in list(indexes)[:n]]  # +2 => header is row 1


def validate_raw_data_csv(file_path: str) -> Tuple[bool, str]:
    try:
        p = Path(file_path)
        if not p.exists():
            return False, f"File not found: {file_path}"
        if p.suffix.lower() != ".csv":
            return False, "File must have .csv extension"

        # Read CSV and normalize headers; drop unnamed/blank header columns (common when trailing commas exist)
        df = pd.read_csv(file_path, low_memory=False)
        raw_cols = list(df.columns)
        keep_mask = [bool(str(c).strip()) and not str(c).lower().startswith("unnamed") for c in raw_cols]
        df = df.loc[:, [c for c, k in zip(raw_cols, keep_mask) if k]]
        df.columns = [str(c).strip() for c in df.columns]

        # Must have at least 2 columns: Sample Name + one grain-size bin
        if len(df.columns) < 2:
            return False, "File must have at least 2 columns: 'Sample Name' and at least one grain-size bin"

        # First column must be exactly 'Sample Name' (case-sensitive)
        first_col = str(df.columns[0]).strip()
        if first_col != "Sample Name":
            return False, f"First column must be 'Sample Name', found '{first_col}'"

        # Parse grain-size header columns as floats and ensure strictly ascending
        bin_headers = df.columns[1:]
        bad_headers = []
        numeric_bins: List[float] = []
        for h in bin_headers:
            try:
                numeric_bins.append(float(str(h).strip()))
            except Exception:
                bad_headers.append(h)
        if bad_headers:
            return False, (
                "One or more grain-size headers are not numeric: "
                f"{[str(h) for h in bad_headers[:10]]} (showing up to 10)."
            )
        if len(numeric_bins) == 0:
            return False, "No grain-size columns found after 'Sample Name'"

        # Require at least one data row
        if df.shape[0] < 1:
            return False, "No data rows found"

        # Sample names must be non-empty and unique
        samples = df["Sample Name"].astype(str).str.strip()
        if samples.eq("").any():
            rows = _first_n_rows(samples[samples.eq("")].index)
            return False, f"Empty 'Sample Name' at rows: {rows} (showing up to 5)."

        # Validate data values: numeric, no missing values
        data_df = df.loc[:, bin_headers]
        # Attempt numeric conversion; detect non-numeric/missing
        converted = data_df.apply(pd.to_numeric, errors="coerce")
        bad_cells = converted.isna()
        if bad_cells.any().any():
            # Identify up to first 5 problematic cells
            problems = []
            for r_idx, c_idx in zip(*np.where(bad_cells.values)):
                row_no = int(bad_cells.index[r_idx]) + 2  # +2 => header row 1
                col_name = bad_cells.columns[c_idx]
                problems.append(f"row {row_no}, column '{col_name}'")
                if len(problems) >= 5:
                    break
            return False, (
                "Found non-numeric or missing values in data cells: "
                f"{problems} (showing up to 5)."
            )

        return True, ""

    except Exception as e:
        return False, f"Error reading file: {str(e)}"
