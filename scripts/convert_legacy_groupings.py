#!/usr/bin/env python3
"""
Parse legacy EntropyMax output CSV (grouped pages with repeated headers and
trailing metrics) and convert to the processed CSV layout expected by the
frontend/Parquet:

Output columns:
  K, Group, Sample, <bin columns...>,
  % explained, Total inequality, Between region inequality,
  Total sum of squares, Within group sum of squares,
  Calinski-Harabasz pseudo-F statistic

Usage:
  python scripts/convert_legacy_groupings.py \
    --legacy data/raw/legacy_outputs/sample_group_3_output.csv \
    --out data/processed/sample_group_3_converted.csv \
    [--gps data/raw/gps/sample_group_3_coordinates.csv]
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


METRIC_NAMES = [
    "% explained",
    "Total inequality",
    "Between region inequality",
    "Total sum of squares",
    "Within group sum of squares",
    "Calinski-Harabasz pseudo-F statistic",
]


def _to_float(s: str) -> float:
    s2 = (s or "").strip()
    if s2 == "":
        return 0.0
    try:
        return float(s2)
    except Exception:
        # Last resort: strip any stray characters
        s3 = re.sub(r"[^0-9eE+\-.]", "", s2)
        try:
            return float(s3) if s3 else 0.0
        except Exception:
            return 0.0


def extract_k_from_banner(line: str) -> Optional[int]:
    # e.g., "Data groupings for  5  groups"
    m = re.search(r"Data\s+groupings\s+for\s+(\d+)\s+groups", line, re.I)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None


def parse_legacy(legacy_path: Path) -> Dict[str, Any]:
    lines = legacy_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # First pass: gather K if present in banner lines
    banner_k: Optional[int] = None
    for ln in lines[:10]:  # banner typically near top
        k = extract_k_from_banner(ln)
        if k is not None:
            banner_k = k
            break

    # Second pass: CSV parse to find headers and data rows (track per-page K)
    rows: List[Dict[str, Any]] = []
    bin_headers: List[str] = []

    reader = csv.reader(lines)
    current_k: Optional[int] = banner_k
    for row in reader:
        if not row:
            continue
        # normalize tokens
        toks = [t.strip() for t in row]

        # Detect page banner lines even if comma-separated
        raw_line = ",".join(row)
        maybe_k_any = extract_k_from_banner(raw_line)
        if maybe_k_any is not None:
            current_k = maybe_k_any
            continue

        # Detect page banner lines that announce K
        if len(toks) == 1:
            maybe_k = extract_k_from_banner(toks[0])
            if maybe_k is not None:
                current_k = maybe_k
                continue
        if len(toks) >= 2 and toks[0].lower() == "group" and toks[1].lower().startswith("sample"):
            # header line: bins start after Sample, allow an optional empty token
            remaining = toks[2:]
            # drop trailing empties
            while remaining and remaining[-1] == "":
                remaining.pop()
            bin_headers = [h for h in remaining if h != ""]
            continue

        # Metric lines: capture at end; keep parsing data rows until then
        line_str = ",".join(toks)
        if re.search(r"%\s*explained", line_str, re.I) or re.search(r"Calinski-Harabasz", line_str, re.I):
            # Defer metrics to a separate pass on raw text
            continue

        # Data line: begins with numeric group followed by sample name
        if toks and re.fullmatch(r"-?\d+", toks[0]):
            grp = int(toks[0])
            samp = toks[1].strip()
            # Some legacy rows have an extra empty placeholder right after Sample
            data_start_idx = 2
            if len(toks) > 2 and toks[2] == "":
                data_start_idx = 3
            values = toks[data_start_idx:]
            # Trim to current bin_headers length, padding if needed
            if bin_headers:
                values = (values + [""] * (len(bin_headers) - len(values)))[: len(bin_headers)]
            rows.append({
                "K": current_k,
                "Group": grp,
                "Sample": samp,
                "values": [_to_float(v) for v in values],
            })

    # Third pass: extract metrics from tail text (apply to all rows)
    text = "\n".join(lines)
    # % explained: starts a line, may have commas after the number
    m_pct = re.search(r"(^|\n)\s*([\d.]+)\s*,?\s*%\s*explained", text, re.I)
    pct_explained = float(m_pct.group(2)) if m_pct else 0.0

    # Inequalities on one line
    m_ti = re.search(r"Total\s+inequality\s+([\d.]+)", text, re.I)
    m_bi = re.search(r"Between\s+region\s+inequality\s+([\d.]+)", text, re.I)
    total_ineq = float(m_ti.group(1)) if m_ti else 0.0
    between_ineq = float(m_bi.group(1)) if m_bi else 0.0

    # Sum of squares line
    m_tot_ss = re.search(r"Total\s+sum\s+of\s+squares[:\s]+([\d.]+)", text, re.I)
    m_within_ss = re.search(r"Within\s+group\s+sum\s+of\s+squares[:\s]+([\d.]+)", text, re.I)
    total_ss = float(m_tot_ss.group(1)) if m_tot_ss else 0.0
    within_ss = float(m_within_ss.group(1)) if m_within_ss else 0.0

    # CH
    m_ch = re.search(r"Calinski-?Harabasz\s+pseudo-?F\s+statistic[:\s]+([\d.]+)", text, re.I)
    ch_val = float(m_ch.group(1)) if m_ch else 0.0

    # Determine a fallback K if none detected for a row
    K_fallback = banner_k if banner_k is not None else max((r.get("Group", 0) for r in rows), default=0)

    # Assemble processed rows
    processed_cols = ["K", "Group", "Sample"] + bin_headers + METRIC_NAMES
    processed: List[List[Any]] = []
    for r in rows:
        k_row = r.get("K", K_fallback) or K_fallback
        base = [k_row, r["Group"], r["Sample"]]
        base.extend(r["values"])  # bins
        base.extend([
            pct_explained,
            total_ineq,
            between_ineq,
            total_ss,
            within_ss,
            ch_val,
        ])
        processed.append(base)

    return {
        "columns": processed_cols,
        "rows": processed,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gps", required=False, help="Optional GPS CSV to append latitude/longitude")
    args = ap.parse_args()

    res = parse_legacy(Path(args.legacy))

    # Optional GPS enrichment
    gps_map: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    if args.gps:
        gps_path = Path(args.gps)
        if not gps_path.exists():
            raise SystemExit(f"GPS file not found: {gps_path}")
        # Read GPS CSV and normalize columns
        with gps_path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            r = csv.DictReader(f)
            # Find columns by fuzzy match
            cols = [c for c in (r.fieldnames or [])]
            def _find(sub: str) -> Optional[str]:
                for c in cols:
                    if sub.lower() in c.lower().strip():
                        return c
                return None
            c_sample = _find("sample") or _find("sample name")
            c_lat = _find("latitude")
            c_lon = _find("longitude")
            if not (c_sample and c_lat and c_lon):
                raise SystemExit("GPS CSV must include Sample, Latitude and Longitude columns")
            for row in r:
                key = str(row.get(c_sample, "")).strip()
                if key and key not in gps_map:
                    try:
                        lat = float(str(row.get(c_lat, "")).strip())
                    except Exception:
                        lat = None
                    try:
                        lon = float(str(row.get(c_lon, "")).strip())
                    except Exception:
                        lon = None
                    gps_map[key] = (lat, lon)

    # Ensure latitude/longitude columns exist in the output schema
    if "latitude" not in res["columns"] and "longitude" not in res["columns"]:
        res["columns"] = list(res["columns"]) + ["latitude", "longitude"]

    # Write CSV
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(res["columns"])
        for row in res["rows"]:
            # row layout: [K, Group, Sample, bins..., metrics...]
            sample = str(row[2]).strip() if len(row) > 2 else ""
            if gps_map:
                lat, lon = gps_map.get(sample, (None, None))
                # Default to -1.0 if missing
                lat_out = -1.0 if lat is None else lat
                lon_out = -1.0 if lon is None else lon
                row_out = list(row) + [lat_out, lon_out]
                w.writerow(row_out)
            else:
                # No GPS provided: emit -1.0 for all rows
                row_out = list(row) + [-1.0, -1.0]
                w.writerow(row_out)
    print(f"Wrote {out_path} with {len(res['rows'])} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


