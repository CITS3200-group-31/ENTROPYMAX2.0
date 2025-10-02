#!/usr/bin/env python3
"""
Quick CSV -> Parquet converter for EntropyMax frontend workflows.

Usage:
  python -m frontend.csv_to_parquet --input output.csv --output data/parquet/output.parquet

Notes:
  - Requires pandas and pyarrow (already in frontend/requirements.txt).
  - Creates the output directory if needed.
  - Keeps column order and types as inferred by pandas; index is not written.
"""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert CSV to Parquet")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output Parquet file (e.g., data/parquet/output.parquet)",
    )
    parser.add_argument(
        "--compression",
        default="snappy",
        choices=["snappy", "gzip", "brotli", "zstd", "none"],
        help="Parquet compression codec (default: snappy)",
    )
    return parser.parse_args(argv)


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Input CSV not found: {args.input}", file=sys.stderr)
        return 2

    compression = None if args.compression == "none" else args.compression

    try:
        # Parse CSV with robust defaults; preserve column order
        df = pd.read_csv(args.input, low_memory=False)
    except Exception as exc:
        print(f"Failed to read CSV: {exc}", file=sys.stderr)
        return 1

    try:
        ensure_parent_dir(args.output)
        df.to_parquet(args.output, index=False, engine="pyarrow", compression=compression)
    except Exception as exc:
        print(f"Failed to write Parquet: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote Parquet: {args.output} from {args.input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


