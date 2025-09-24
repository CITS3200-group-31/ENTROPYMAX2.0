#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


SegmentMeta = Tuple[int, float, float, float, float, float, int, float]


def parse_segments(lines: List[str]) -> List[Tuple[int, int, int, SegmentMeta]]:
    segments: List[Tuple[int, int, int, SegmentMeta]] = []

    re_k = re.compile(r"^Data groupings for\s+(\d+)\s+groups\s*$")
    re_pct = re.compile(r"^\s*([0-9.+-Ee]+)\s*,\s*% explained\s*$")
    re_ineq = re.compile(r"^Total inequality\s+([0-9.+-Ee]+)\s+\s*Between region inequality\s+([0-9.+-Ee]+)\s*$")
    re_sumsq = re.compile(r"^Total sum of squares:\s*([0-9.+-Ee]+)\s+Within group sum of squares:\s*([0-9.+-Ee]+)\s*$")
    re_ch = re.compile(r"^Calinski-Harabasz pseudo-F statistic:\s*([0-9.+-Ee]+)\s*$")

    idx = 0
    n = len(lines)
    while idx < n:
        m_k = re_k.match(lines[idx].strip())
        if not m_k:
            idx += 1
            continue
        k_val = int(m_k.group(1))

        # Expect header at idx+2 (after current line, there is likely a blank line)
        # Scan forward until we find the next header starting with Group,Sample
        header_idx = None
        for j in range(idx + 1, min(idx + 10, n)):
            if lines[j].lstrip().startswith("Group,Sample"):
                header_idx = j
                break
        if header_idx is None:
            idx += 1
            continue

        # Data rows until we hit a line ending with '% explained'
        data_start = header_idx + 1
        data_end = data_start
        while data_end < n and not re_pct.match(lines[data_end].strip()):
            data_end += 1
        if data_end >= n:
            break

        # Now parse trailing metadata block
        m_pct = re_pct.match(lines[data_end].strip())
        pct_explained = float(m_pct.group(1)) if m_pct else float("nan")

        m_ineq = re_ineq.match(lines[data_end + 1].strip()) if data_end + 1 < n else None
        total_inequality = float(m_ineq.group(1)) if m_ineq else float("nan")
        between_region_inequality = float(m_ineq.group(2)) if m_ineq else float("nan")

        m_sumsq = re_sumsq.match(lines[data_end + 2].strip()) if data_end + 2 < n else None
        total_ss = float(m_sumsq.group(1)) if m_sumsq else float("nan")
        within_ss = float(m_sumsq.group(2)) if m_sumsq else float("nan")

        m_ch = re_ch.match(lines[data_end + 3].strip()) if data_end + 3 < n else None
        ch_stat = float(m_ch.group(1)) if m_ch else float("nan")

        num_samples = data_end - data_start
        meta: SegmentMeta = (
            k_val,
            pct_explained,
            total_inequality,
            between_region_inequality,
            total_ss,
            within_ss,
            num_samples,
            ch_stat,
        )
        segments.append((data_start, data_end, header_idx, meta))

        idx = data_end + 4

    return segments


def load_coordinates(coords_path: Path) -> Dict[str, Tuple[str, str]]:
    mapping: Dict[str, Tuple[str, str]] = {}
    with coords_path.open("r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n")
        # Expect 'Sample Name,Latitude,Longitude'
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            name = parts[0]
            lat = parts[1]
            lon = parts[2]
            mapping[name] = (lat, lon)
    return mapping


def split_csv_row(line: str) -> List[str]:
    # The input rows are simple comma-separated with extra spaces; no embedded commas in quoted fields.
    return [c.strip() for c in line.split(",")]


def trim_trailing_empty(columns: List[str]) -> List[str]:
    # Remove one or more trailing empty columns that may come from a trailing comma
    while columns and columns[-1] == "":
        columns.pop()
    return columns


def main(argv: List[str]) -> int:
    root = Path(__file__).resolve().parents[1]
    in_path = root / "data" / "processed" / "sample_output.csv"
    coords_path = root / "data" / "raw" / "sample_coordinates.csv"
    out_path = root / "data" / "processed" / "sample_output_augmented.csv"

    if len(argv) >= 2:
        in_path = Path(argv[1])
    if len(argv) >= 3:
        coords_path = Path(argv[2])
    if len(argv) >= 4:
        out_path = Path(argv[3])

    lines = in_path.read_text(encoding="utf-8").splitlines()
    segments = parse_segments(lines)
    coords = load_coordinates(coords_path)

    # Build output
    header_cols: Optional[List[str]] = None
    out_lines: List[str] = []

    for data_start, data_end, header_idx, meta in segments:
        k_val, pct, tot_in, betw_in, tss, wss, n_samples, ch_stat = meta
        # Parse header once
        in_header = lines[header_idx].strip()
        in_cols = trim_trailing_empty(split_csv_row(in_header))
        if header_cols is None:
            header_cols = in_cols + [
                "Total Inequality",
                "Between Region Inequality",
                "Total Sum Of Squares",
                "Within Group Sum Of Squares",
                "Calinski-Harabasz pseudo-F statistic",
                "% Explained",
                "K",
                "Latitude",
                "Longitude",
            ]
            out_lines.append(",".join(header_cols))

        # Emit rows with appended metadata
        for i in range(data_start, data_end):
            row = lines[i].strip()
            if not row:
                continue
            # Expect first two fields: Group, Sample
            cols = trim_trailing_empty(split_csv_row(row))
            if cols and cols[0].strip().lower() == "group":
                # Defensive: skip any stray header lines from source
                continue
            if len(cols) < 2:
                continue
            sample_name = cols[1]
            lat, lon = coords.get(sample_name, ("", ""))
            augmented = cols + [
                f"{tot_in}",
                f"{betw_in}",
                f"{tss}",
                f"{wss}",
                f"{ch_stat}",
                f"{pct}",
                f"{k_val}",
                lat,
                lon,
            ]
            out_lines.append(",".join(augmented))
    out_text = "\n".join(out_lines) + "\n"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"Wrote {out_path} with {len(out_lines)-1} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


