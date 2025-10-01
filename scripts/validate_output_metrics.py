#!/usr/bin/env python3
"""
Validate EntropyMax backend output against first-principles metric recomputation.

Given:
  --input  path/to/input.csv           (raw input used to produce the output)
  --output path/to/sample_outputt.csv  (backend CSV output with K pages)

This script:
  1) Loads the input CSV, trims names, and builds a matrix of raw values
  2) Applies the same preprocessing used by the backend (grand-total percent only)
  3) For each K page in the output, reconstructs group assignments and recomputes:
       - tineq (total inequality)
       - bineq (between-group inequality)
       - Rs = 100 * bineq / tineq
       - SST, SSE and CH = ((SST-SSE)/(K-1)) / (SSE/(N-K))
  4) Compares computed vs reported metrics within tolerance and exits non-zero on any mismatch

Usage:
  python scripts/validate_output_metrics.py \
      --input data/input.csv \
      --output data/processed/sample_outputt.csv \
      [--k 4] [--tol 1e-6]

Notes:
  - The script assumes the output header begins with: K,Group,Sample,<bin headers...>, then metrics
  - Metrics are expected in this order:
       % explained, Total inequality, Between region inequality,
       Total sum of squares, Within group sum of squares,
       Calinski-Harabasz pseudo-F statistic
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict, OrderedDict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


METRIC_NAMES = [
    "% explained",
    "Total inequality",
    "Between region inequality",
    "Total sum of squares",
    "Within group sum of squares",
    "Calinski-Harabasz pseudo-F statistic",
]


def log2(x: float) -> float:
    return math.log(x, 2.0)


def load_input_matrix(path: Path) -> Tuple[List[str], List[str], List[List[float]]]:
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        cols = [c.strip() for c in header]
        # Determine sample column
        try:
            sample_idx = next(i for i, c in enumerate(cols) if c.lower() in ("sample", "sample name"))
        except StopIteration:
            raise SystemExit("Input CSV must have Sample or Sample Name column")
        bin_headers = [h for i, h in enumerate(header) if i != sample_idx]
        samples: List[str] = []
        matrix: List[List[float]] = []
        for row in r:
            if not row:
                continue
            s = str(row[sample_idx]).strip()
            values: List[float] = []
            for i, tok in enumerate(row):
                if i == sample_idx:
                    continue
                try:
                    v = float(str(tok).strip() or 0.0)
                except Exception:
                    v = 0.0
                values.append(v)
            samples.append(s)
            matrix.append(values)
        return bin_headers, samples, matrix


def preprocess_gdtl_percent(matrix: List[List[float]]) -> List[List[float]]:
    total = 0.0
    for row in matrix:
        for v in row:
            total += v
    if total <= 0.0:
        return [[0.0 for _ in row] for row in matrix]
    scale = 100.0 / total
    return [[v * scale for v in row] for row in matrix]


def total_inequality(data: List[List[float]]) -> Tuple[List[float], float]:
    # data: N x M
    n = len(data)
    if n == 0:
        return [], 0.0
    m = len(data[0]) if data else 0
    Y = [0.0] * m
    for j in range(m):
        Y[j] = sum(data[i][j] for i in range(n))
    tineq = 0.0
    for j in range(m):
        Yj = Y[j]
        if Yj == 0.0:
            continue
        X = 0.0
        for i in range(n):
            val = data[i][j]
            if val > 0.0:
                ratio = val / Yj
                argument = (n * val) / Yj
                if argument > 0.0:
                    X += ratio * log2(argument)
        tineq += Yj * X
    return Y, tineq


def between_inequality(data: List[List[float]], Y: List[float], groups01: List[int], k: int) -> float:
    n = len(data)
    m = len(data[0]) if data else 0
    # yr(group, j) and nr(group)
    nr = [0] * k
    yr = [[0.0] * m for _ in range(k)]
    for i in range(n):
        g = groups01[i]
        if g < 0 or g >= k:
            continue
        nr[g] += 1
        for j in range(m):
            yr[g][j] += data[i][j]
    # Normalize by Y[j]
    for g in range(k):
        for j in range(m):
            if Y[j] > 0.0:
                yr[g][j] = yr[g][j] / Y[j]
            else:
                yr[g][j] = 0.0
    bineq = 0.0
    for j in range(m):
        Yj = Y[j]
        if Yj == 0.0:
            continue
        bineq2 = 0.0
        for g in range(k):
            if nr[g] == 0:
                continue
            if yr[g][j] == 0.0:
                continue
            arg = yr[g][j] * (n / nr[g])
            if arg > 0.0:
                bineq2 += yr[g][j] * log2(arg)
        bineq += Yj * bineq2
    return bineq


def sst_sse_ch(data: List[List[float]], groups01: List[int], k: int) -> Tuple[float, float, float]:
    n = len(data)
    m = len(data[0]) if data else 0
    # Totals and averages
    totsum = [0.0] * m
    for j in range(m):
        for i in range(n):
            totsum[j] += data[i][j]
    totav = [t / n for t in totsum]

    # Group sums and counts
    clsum = [[0.0] * m for _ in range(k)]
    clsam = [0.0] * k
    for i in range(n):
        g = groups01[i]
        if g < 0 or g >= k:
            continue
        clsam[g] += 1.0
        for j in range(m):
            clsum[g][j] += data[i][j]

    # Group averages
    clav = [[0.0] * m for _ in range(k)]
    for g in range(k):
        if clsam[g] == 0:
            continue
        for j in range(m):
            clav[g][j] = clsum[g][j] / clsam[g]

    # SST and SSE
    sst = [0.0] * m
    sse = 0.0
    for j in range(m):
        for i in range(n):
            v = data[i][j]
            sst[j] += (v - totav[j]) ** 2
            g = groups01[i]
            if 0 <= g < k and clsam[g] > 0.0:
                sse += (v - clav[g][j]) ** 2
    sstt = sum(sst)

    # CH
    r = (sstt - sse) / sstt if sstt > 0 else 0.0
    if r == 1.0:
        ch = float("inf")
    else:
        numerator = (sstt - sse) / (k - 1) if k > 1 else 0.0
        denominator = (sse / (n - k)) if (n - k) > 0 else float("inf")
        ch = numerator / denominator if denominator > 0 else float("inf")
    return sstt, sse, ch


def find_output_layout(header: List[str]) -> Tuple[int, int, List[int], Dict[str, int]]:
    cols = [c.strip() for c in header]
    try:
        k_idx = cols.index("K")
        g_idx = cols.index("Group")
        s_idx = cols.index("Sample")
    except ValueError:
        raise SystemExit("Output header must include K, Group, Sample")
    # Bin columns: from Sample+1 until first metric name
    metric_indices: Dict[str, int] = {}
    end = len(cols)
    for name in METRIC_NAMES:
        if name in cols:
            idx = cols.index(name)
            metric_indices[name] = idx
            end = min(end, idx)
    if not metric_indices:
        raise SystemExit("Output header missing metric columns")
    bin_idx = list(range(s_idx + 1, end))
    return k_idx, g_idx, bin_idx, metric_indices


def approx_equal(a: float, b: float, tol: float) -> bool:
    if math.isinf(a) or math.isinf(b) or math.isnan(a) or math.isnan(b):
        return a == b
    if abs(a - b) <= tol:
        return True
    # Relative tolerance fallback
    denom = max(1.0, abs(a), abs(b))
    return abs(a - b) / denom <= tol


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--k", type=int, default=None, help="Validate only this K page")
    ap.add_argument("--tol", type=float, default=1e-6)
    args = ap.parse_args()

    # Load input and preprocess
    in_bins, in_samples, in_matrix_raw = load_input_matrix(Path(args.input))
    in_matrix = preprocess_gdtl_percent(in_matrix_raw)
    n = len(in_samples)
    m = len(in_bins)

    # Index map from sample name to one or more input row indices (to support duplicates)
    name_to_indices: Dict[str, List[int]] = {}
    for i, s in enumerate(in_samples):
        name_to_indices.setdefault(s, []).append(i)

    # Read output and group by K
    with Path(args.output).open("r", encoding="utf-8", errors="ignore", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        k_idx, g_idx, bin_idx, metric_indices = find_output_layout(header)
        pages: Dict[int, List[Tuple[str, int]]] = defaultdict(list)
        reported: Dict[int, Tuple[float, float, float, float, float, float]] = {}

        # Metrics indices
        idx_pct = metric_indices[METRIC_NAMES[0]]
        idx_tineq = metric_indices[METRIC_NAMES[1]]
        idx_bineq = metric_indices[METRIC_NAMES[2]]
        idx_sst = metric_indices[METRIC_NAMES[3]]
        idx_sse = metric_indices[METRIC_NAMES[4]]
        idx_ch = metric_indices[METRIC_NAMES[5]]

        for row in r:
            if not row:
                continue
            try:
                k = int(str(row[k_idx]).strip())
            except Exception:
                continue
            if args.k is not None and k != args.k:
                continue
            sample = str(row[g_idx + 1]).strip()  # Sample is right after Group
            try:
                g = int(str(row[g_idx]).strip())
            except Exception:
                continue
            pages[k].append((sample, g))
            # Capture metrics once per K (from the first encountered row)
            if k not in reported:
                try:
                    pct = float(row[idx_pct])
                    ti = float(row[idx_tineq])
                    bi = float(row[idx_bineq])
                    sst = float(row[idx_sst])
                    sse = float(row[idx_sse])
                    ch = float(row[idx_ch])
                    reported[k] = (pct, ti, bi, sst, sse, ch)
                except Exception:
                    pass

    failures = 0

    for k, assignments in sorted(pages.items()):
        # Build group vector aligned to input order (support duplicate sample names)
        groups01 = [-1] * n
        # Work on a fresh copy so we don't mutate the master mapping across K pages
        pending: Dict[str, List[int]] = {k2: v2.copy() for k2, v2 in name_to_indices.items()}
        for sample, g1 in assignments:
            lst = pending.get(sample)
            if not lst:
                print(f"[K={k}] Sample not found or exhausted in input: {sample}")
                failures += 1
                continue
            i = lst.pop(0)
            groups01[i] = max(0, g1 - 1)
        if any(g < 0 for g in groups01):
            missing = [in_samples[i] for i, g in enumerate(groups01) if g < 0]
            print(f"[K={k}] Missing group assignments for {len(missing)} samples (e.g., {missing[:3]})")
            failures += 1
            continue

        # Compute metrics
        Y, tineq = total_inequality(in_matrix)
        bineq = between_inequality(in_matrix, Y, groups01, k)
        rs = (bineq / tineq) * 100.0 if tineq > 0.0 else 0.0
        sstt, sse, ch = sst_sse_ch(in_matrix, groups01, k)

        if k not in reported:
            print(f"[K={k}] No reported metrics found in output header row")
            failures += 1
            continue
        rpt_pct, rpt_ti, rpt_bi, rpt_sst, rpt_sse, rpt_ch = reported[k]

        def check(name: str, comp: float, rpt: float):
            nonlocal failures
            if not approx_equal(comp, rpt, args.tol):
                print(f"[K={k}] {name} mismatch: computed={comp:.9f}, reported={rpt:.9f}")
                failures += 1

        check("Total inequality", tineq, rpt_ti)
        check("Between inequality", bineq, rpt_bi)
        check("Rs (% explained)", rs, rpt_pct)
        check("SST", sstt, rpt_sst)
        check("SSE", sse, rpt_sse)
        check("CH", ch, rpt_ch)

    if failures:
        print(f"Validation FAILED with {failures} mismatches")
        return 1
    print("Validation PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


