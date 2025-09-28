#!/usr/bin/env python3
"""
Reconstruct an input CSV (Sample + bin columns) from one or more processed
EntropyMax output CSVs.

Assumptions about input (output) CSVs:
- Columns begin with: K, Group, Sample, <bin columns...>, metrics..., [latitude, longitude]
- Bin columns are exactly the header tokens between 'Sample' and the first
  metric/K/latitude/longitude column. We preserve those bin headers as-is.
- Rows may span multiple K pages. We optionally filter by a specific K, and
  we deduplicate on (Sample, full bin-vector) preserving first occurrence.

Usage:
  python scripts/input_from_output.py \
    --out data/reconstructed_input.csv \
    [--k 4] \
    data/processed/sample_outputt.csv [more_output.csv ...]

Output:
- CSV with columns: Sample,<bin headers...>
- Also writes a coordinates CSV alongside the output, named <out_basename>_coordinates.csv
  with columns: Sample,Latitude,Longitude and values set to -1.0 (unknown).

Notes:
- Trims whitespace in Sample names before dedupe.
- If multiple input files are provided, their bin headers must match exactly.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Tuple, Dict, Optional


METRIC_NAMES = [
    "% explained",
    "Total inequality",
    "Between region inequality",
    "Total sum of squares",
    "Within group sum of squares",
    "Calinski-Harabasz pseudo-F statistic",
]

KNOWN_TRAILERS = set(["K", "latitude", "longitude"]) | set(METRIC_NAMES)


def find_indices(header: List[str]) -> Tuple[int, List[int]]:
    """Return sample column index and list of bin column indices.

    We detect bin columns as the contiguous block after Sample/Sample Name up to
    (but not including) the first known trailer column (metrics, K, latitude, longitude).
    """
    # Normalize header tokens for matching but preserve originals for output
    norm = [str(h).strip() for h in header]

    # Sample column
    try:
        sample_idx = next(i for i, h in enumerate(norm) if h.lower() in ("sample", "sample name"))
    except StopIteration:
        raise SystemExit("Could not find 'Sample' or 'Sample Name' column in output header")

    # Determine where bin columns end
    end_idx = len(header)
    for i in range(sample_idx + 1, len(header)):
        token = norm[i]
        if token in KNOWN_TRAILERS:
            end_idx = i
            break
    # Bin columns are [sample_idx+1, end_idx)
    if end_idx <= sample_idx + 1:
        raise SystemExit("Could not infer bin columns between Sample and metrics/K")
    bin_indices = list(range(sample_idx + 1, end_idx))
    return sample_idx, bin_indices


def read_rows(path: Path, want_k: Optional[int]) -> Tuple[List[str], List[Tuple[str, Tuple[str, ...]]]]:
    """Read output CSV and return (bin_headers, rows) where rows are (sample, bin_values_as_strings).
    Filters by K if want_k is provided and a K column exists.
    """
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        r = csv.reader(f)
        try:
            header = next(r)
        except StopIteration:
            return [], []
        sample_idx, bin_idx = find_indices(header)

        # Locate K column if present
        header_norm = [str(h).strip() for h in header]
        k_idx = next((i for i, h in enumerate(header_norm) if h == "K"), None)

        # Build bin headers list exactly as in the file
        bin_headers = [header[i] for i in bin_idx]

        rows: List[Tuple[str, Tuple[str, ...]]] = []
        for row in r:
            if not row:
                continue
            if k_idx is not None and want_k is not None:
                try:
                    if int(str(row[k_idx]).strip() or 0) != want_k:
                        continue
                except Exception:
                    continue
            sample = str(row[sample_idx]).strip()
            # Extract bin values as strings, trimming whitespace but preserving token text
            vals = tuple(str(row[i]).strip() for i in bin_idx)
            rows.append((sample, vals))
    return bin_headers, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("outputs", nargs="+", help="One or more processed output CSV files")
    ap.add_argument("--out", required=True, help="Path to write reconstructed input CSV")
    ap.add_argument("--k", type=int, default=None, help="Optional K filter (only keep rows for this K)")
    args = ap.parse_args()

    bin_headers_all: Optional[List[str]] = None
    # Use ordered dict keyed by (sample, vector) to dedupe while preserving order
    seen: Dict[Tuple[str, Tuple[str, ...]], None] = {}

    for p in args.outputs:
        path = Path(p)
        if not path.exists():
            raise SystemExit(f"Output CSV not found: {path}")
        bin_headers, rows = read_rows(path, args.k)
        if bin_headers_all is None:
            bin_headers_all = bin_headers
        else:
            if bin_headers_all != bin_headers:
                raise SystemExit(
                    f"Bin headers mismatch across files. First={bin_headers_all[:5]}..., this={bin_headers[:5]}..."
                )
        for sample, vec in rows:
            key = (sample, vec)
            if key not in seen:
                seen[key] = None

    if bin_headers_all is None:
        raise SystemExit("No data found in provided output CSVs")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write reconstructed input CSV
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # Input header: Sample + exact bin headers
        w.writerow(["Sample"] + bin_headers_all)
        samples_in_order: List[str] = []
        seen_samples: Dict[str, None] = {}
        for (sample, vec) in seen.keys():
            w.writerow([sample] + list(vec))
            if sample not in seen_samples:
                seen_samples[sample] = None
                samples_in_order.append(sample)

    print(f"Wrote {out_path} with {len(seen)} unique rows and {len(bin_headers_all)} bin columns")

    # Write companion coordinates CSV with -1.0 defaults
    coords_path = out_path.with_name(out_path.stem + "_coordinates.csv")
    with coords_path.open("w", newline="", encoding="utf-8") as fcoords:
        wc = csv.writer(fcoords)
        wc.writerow(["Sample", "Latitude", "Longitude"])
        for sample in samples_in_order:
            wc.writerow([sample, -1.0, -1.0])
    print(f"Wrote {coords_path} with {len(samples_in_order)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


