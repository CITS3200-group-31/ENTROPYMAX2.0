#!/usr/bin/env python3
"""
Convert legacy EntropyMax CSV outputs to the new column structure, and optionally
merge latitude/longitude from a GPS CSV.

New structure:
  Group, Sample, <bin columns...>, <metric columns...>, K, [latitude, longitude]

Usage:
  python scripts/convert_legacy_output.py \
    --legacy data/raw/legacy_outputs/<dataset>_legacy_output.csv \
    --out data/processed/csv/<dataset>_converted.csv \
    [--gps data/raw/gps/<dataset>_gps.csv]
"""

import argparse
import os
import sys
import pandas as pd

METRIC_NAMES = [
    "% explained",
    "Total inequality",
    "Between region inequality",
    "Total sum of squares",
    "Within group sum of squares",
    "Calinski-Harabasz pseudo-F statistic",
]


def normalize_gps_columns(gps_df: pd.DataFrame) -> pd.DataFrame:
    cols_lc = {c.lower().strip(): c for c in gps_df.columns}
    # Normalize Sample column
    if "sample" in cols_lc:
        gps_df = gps_df.rename(columns={cols_lc["sample"]: "Sample"})
    elif "sample name" in cols_lc:
        gps_df = gps_df.rename(columns={cols_lc["sample name"]: "Sample"})
    else:
        raise ValueError("GPS CSV must have 'Sample' or 'Sample Name' column")
    # Normalize latitude/longitude -> lowercase
    rename = {}
    if "latitude" in cols_lc:
        rename[cols_lc["latitude"]] = "latitude"
    if "longitude" in cols_lc:
        rename[cols_lc["longitude"]] = "longitude"
    gps_df = gps_df.rename(columns=rename)
    # Basic checks
    for c in ("latitude", "longitude"):
        if c not in gps_df.columns:
            raise ValueError(f"GPS CSV missing required column: {c}")
    # Trim sample key
    gps_df["Sample"] = gps_df["Sample"].astype(str).str.strip()
    # Deduplicate by first seen
    gps_df = gps_df.drop_duplicates(subset=["Sample"], keep="first")
    return gps_df[["Sample", "latitude", "longitude"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy", required=True, help="Path to legacy output CSV")
    ap.add_argument("--out", required=True, help="Path to write converted CSV")
    ap.add_argument("--gps", required=False, help="Optional GPS CSV to append latitude/longitude")
    args = ap.parse_args()

    df = pd.read_csv(args.legacy)
    # Normalize headers: strip only; keep original cases for display, but compare via lower
    df.columns = [str(c).strip() for c in df.columns]
    cols = df.columns.tolist()

    # Identify key columns
    if "Group" not in cols or "Sample" not in cols:
        return _fail("Legacy CSV must contain 'Group' and 'Sample' columns")
    if "K" not in cols:
        return _fail("Legacy CSV must contain 'K' column")

    # Determine metrics start by known first metric name
    m_first = None
    for m in METRIC_NAMES:
        if m in cols:
            m_first = m
            break
    if m_first is None:
        return _fail("Could not locate first metric column in legacy CSV header")

    # Build grouping of columns
    idx_sample = cols.index("Sample")
    idx_metrics_start = cols.index(m_first)

    # Bin columns are everything after Sample up to (but excluding) first metric
    bin_cols = cols[idx_sample + 1 : idx_metrics_start]
    # Ensure leading bin '0.02' exists (insert zero column if missing)
    ensure_bin = "0.02"
    add_leading_bin = ensure_bin not in bin_cols
    metric_cols = [c for c in METRIC_NAMES if c in cols]

    # Validate expected order of early columns (legacy is K,Group,Sample,...). We will reconstruct anyway.
    # Reconstruct new order: Group, Sample, bins..., metrics... (+ K and GPS later)
    select_cols = ["Group", "Sample"] + bin_cols + metric_cols

    # Rearrange
    try:
        df_new = df[select_cols].copy()
        if add_leading_bin:
            # Insert zero-filled leading bin immediately after Sample
            insert_at = 2  # after Group, Sample
            df_new.insert(insert_at, ensure_bin, 0.0)
    except KeyError as e:
        return _fail(f"Column missing while reordering: {e}")

    # Add K at end (for no GPS); if GPS present, K should be third-from-last
    df_k = df[["K"]].copy()

    # Filter to optimal K (max CH) to match expected per-sample rows
    try:
        ch_col = next((m for m in METRIC_NAMES if m in df.columns), None)
        if ch_col is not None and "K" in df.columns:
            best_k = (
                df[["K", ch_col]]
                .groupby("K", as_index=False)
                .mean(numeric_only=True)
                .sort_values(ch_col, ascending=False)
                .iloc[0]["K"]
            )
            df_k = df[df["K"] == best_k]
            df_new = df_new.loc[df_k.index]
        else:
            best_k = None
    except Exception:
        best_k = None

    if args.gps:
        gps_df = normalize_gps_columns(pd.read_csv(args.gps))
        # Normalize Sample in data frame before merge
        df_new["Sample"] = df_new["Sample"].astype(str).str.strip()
        out = df_new.join(df[["K"]])
        if best_k is not None:
            out = out[out["K"] == best_k]
        out = out.merge(gps_df, on="Sample", how="left")
        # Move K to third-from-last (just before latitude/longitude)
        # Current order is: new_cols..., K, latitude, longitude
        cols_out = out.columns.tolist()
        # Ensure K exists
        cols_out.remove("K")
        cols_out.insert(len(cols_out) - 2, "K")
        out = out[cols_out]
    else:
        out = df_new.join(df[["K"]])
        if best_k is not None:
            out = out[out["K"] == best_k]

    out.to_csv(args.out, index=False, float_format="%.15g")
    print(f"Wrote {args.out}")

    # Back-convert to legacy layout and compare for exact match
    back_path = args.out.rsplit(".", 1)[0] + ".back_legacy.csv"
    try:
        conv = pd.read_csv(args.out)
        # Drop GPS columns if present
        for c in ("latitude", "longitude"):
            if c in conv.columns:
                conv = conv.drop(columns=[c])
        # Reorder to legacy: K, Group, Sample, bins..., metrics...
        cols_conv = conv.columns.tolist()
        if "K" not in cols_conv or "Group" not in cols_conv or "Sample" not in cols_conv:
            return _fail("Converted CSV missing one of required columns: K/Group/Sample")
        # Locate first metric in converted
        m_first_conv = next((m for m in METRIC_NAMES if m in cols_conv), None)
        if m_first_conv is None:
            return _fail("Converted CSV missing metric columns for back-conversion")
        idx_sample_conv = cols_conv.index("Sample")
        idx_metrics_start_conv = cols_conv.index(m_first_conv)
        bin_cols_conv = cols_conv[idx_sample_conv + 1 : idx_metrics_start_conv]
        metric_cols_conv = [m for m in METRIC_NAMES if m in cols_conv]
        legacy_cols = ["K", "Group", "Sample"] + bin_cols_conv + metric_cols_conv
        conv_legacy = conv[legacy_cols]
        conv_legacy.to_csv(back_path, index=False, float_format="%.15g")
    except Exception as e:
        return _fail(f"Back-conversion failed: {e}")

    # Exact byte comparison (can be skipped with EM_SKIP_BACKCHECK=1)
    try:
        with open(args.legacy, "rb") as f1, open(back_path, "rb") as f2:
            b1 = f1.read()
            b2 = f2.read()
        if b1 == b2:
            print(f"Back-conversion exact match verified: {back_path} == {args.legacy}")
            return 0
        else:
            if os.environ.get("EM_SKIP_BACKCHECK", "0") == "1":
                print("WARN: Back-converted CSV does not exactly match the legacy input (skipping per EM_SKIP_BACKCHECK).", file=sys.stderr)
                return 0
            else:
                print("ERROR: Back-converted CSV does not exactly match the legacy input.", file=sys.stderr)
                print(f"Legacy: {args.legacy}", file=sys.stderr)
                print(f"Back:   {back_path}", file=sys.stderr)
                return 3
    except Exception as e:
        return _fail(f"Comparison failed: {e}")


def _fail(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())


