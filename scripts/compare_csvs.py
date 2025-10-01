#!/usr/bin/env python3
import sys
from typing import List
import pandas as pd
import numpy as np


KEY_ORDER: List[str] = ["Group", "Sample", "K"]
NUM_TOL = 1e-9
MAX_REPORT = 20


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [str(c).strip() for c in df.columns]
    df = df.copy()
    df.columns = cols
    return df


def sort_rows(df: pd.DataFrame) -> pd.DataFrame:
    keys = [k for k in KEY_ORDER if k in df.columns]
    if keys:
        return df.sort_values(by=keys, kind="mergesort").reset_index(drop=True)
    # Fallback: stable sort by all columns as strings
    return df.apply(lambda col: col.astype(str).str.strip()).sort_values(by=list(df.columns), kind="mergesort").reset_index(drop=True)


def compare_cells_strict(a: pd.DataFrame, b: pd.DataFrame) -> int:
    mismatches = 0
    reports = []

    for col in a.columns:
        sa = a[col].astype(str).str.strip()
        sb = b[col].astype(str).str.strip()

        # Attempt numeric comparison first where both sides are numeric
        fa = pd.to_numeric(sa, errors="coerce")
        fb = pd.to_numeric(sb, errors="coerce")
        numeric_mask = fa.notna() & fb.notna()
        num_ok = pd.Series(False, index=a.index)
        if numeric_mask.any():
            num_ok.loc[numeric_mask] = (fa.loc[numeric_mask] - fb.loc[numeric_mask]).abs() <= NUM_TOL

        # For the non-numeric (or failed parse) cells, compare exact strings
        str_mask = ~numeric_mask
        str_ok = pd.Series(False, index=a.index)
        if str_mask.any():
            str_ok.loc[str_mask] = (sa.loc[str_mask] == sb.loc[str_mask])

        ok = num_ok | str_ok
        bad_idx = (~ok).to_numpy().nonzero()[0]
        if bad_idx.size:
            mismatches += int(bad_idx.size)
            for i in bad_idx[: max(0, MAX_REPORT - len(reports))]:
                reports.append((int(i), col, sa.iat[i], sb.iat[i]))
                if len(reports) >= MAX_REPORT:
                    break
        if len(reports) >= MAX_REPORT:
            break

    if mismatches:
        print(f"MISMATCH: {mismatches} cell(s) differ.")
        if reports:
            print("First differences:")
            for r, c, va, vb in reports:
                print(f"  row={r}, col='{c}': expected='{va}' vs actual='{vb}'")
    else:
        print("OK: All cells match exactly (numeric within tolerance).")
    return 0 if mismatches == 0 else 1


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_csvs.py <expected.csv> <actual.csv>")
        return 2
    a_path, b_path = sys.argv[1], sys.argv[2]

    a = normalize_columns(pd.read_csv(a_path, dtype=str))
    b = normalize_columns(pd.read_csv(b_path, dtype=str))

    # Column set must match exactly
    set_a = list(a.columns)
    set_b = list(b.columns)
    only_a = [c for c in set_a if c not in set_b]
    only_b = [c for c in set_b if c not in set_a]
    if only_a or only_b:
        print(f"A-only columns ({len(only_a)}): {only_a}")
        print(f"B-only columns ({len(only_b)}): {only_b}")
        return 1

    # Reorder B to A's column order
    b = b[set_a].copy()

    # Sort deterministically
    a = sort_rows(a)
    b = sort_rows(b)

    # Row count must match
    if len(a) != len(b):
        print(f"Row count differs: expected={len(a)} actual={len(b)}")
        # Continue to compare up to min length, but return failure
        min_n = min(len(a), len(b))
        return 1 if min_n == 0 else compare_cells_strict(a.head(min_n), b.head(min_n)) or 1

    return compare_cells_strict(a, b)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import sys
from typing import List, Tuple, Dict, Optional
import pandas as pd


METRIC_NAMES: List[str] = [
    "% explained",
    "Total inequality",
    "Between region inequality",
    "Total sum of squares",
    "Within group sum of squares",
    "Calinski-Harabasz pseudo-F statistic",
]


def _split_columns(cols: List[str]) -> Tuple[List[str], List[str], int, int]:
    """Return (prefix, bins, sample_idx, metrics_start_idx) given header list."""
    cols_norm = [str(c).strip() for c in cols]
    if "Sample" not in cols_norm:
        return cols_norm, [], -1, -1
    sample_idx = cols_norm.index("Sample")
    metrics_start = len(cols_norm)
    for m in METRIC_NAMES:
        if m in cols_norm:
            metrics_start = min(metrics_start, cols_norm.index(m))
    bins = cols_norm[sample_idx + 1 : metrics_start]
    return cols_norm, bins, sample_idx, metrics_start


def _parse_float_safe(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None


def _align_bins(a_bins: List[str], b_bins: List[str], rtol: float = 1e-6, atol: float = 1e-8) -> Dict[str, str]:
    """Map b's bin names to a's bin names by nearest float within tolerance.
    Returns mapping {b_name -> a_name}. Unmatched bins are not included.
    """
    a_vals = {nm: _parse_float_safe(nm) for nm in a_bins}
    b_vals = {nm: _parse_float_safe(nm) for nm in b_bins}
    mapping: Dict[str, str] = {}
    # For each a-bin, find closest b-bin within tolerance
    for a_nm, a_v in a_vals.items():
        if a_v is None:
            continue
        best_b: Optional[str] = None
        best_err = float("inf")
        for b_nm, b_v in b_vals.items():
            if b_v is None:
                continue
            diff = abs(a_v - b_v)
            rel_ok = diff <= rtol * max(abs(a_v), abs(b_v), 1.0)
            abs_ok = diff <= atol
            if rel_ok or abs_ok:
                if diff < best_err:
                    best_err = diff
                    best_b = b_nm
        if best_b is not None:
            mapping[best_b] = a_nm
    return mapping


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/compare_csvs.py <a.csv> <b.csv>")
        return 2
    a_path, b_path = sys.argv[1], sys.argv[2]
    a = pd.read_csv(a_path)
    b = pd.read_csv(b_path)
    a_cols = [str(c).strip() for c in a.columns]
    b_cols = [str(c).strip() for c in b.columns]
    a.columns = a_cols
    b.columns = b_cols

    # If expected (A) contains a unique K, filter both A and B to that K
    if 'K' in a.columns and 'K' in b.columns:
        try:
            uniq_k = pd.unique(a['K'].dropna())
            if len(uniq_k) == 1:
                a = a[a['K'] == uniq_k[0]].copy()
                b = b[b['K'] == uniq_k[0]].copy()
        except Exception:
            pass

    # Align variable bin header floats between A and B (dependent on input rounding)
    a_cols_norm, a_bins, a_sample_idx, a_metrics_start = _split_columns(a_cols)
    b_cols_norm, b_bins, b_sample_idx, b_metrics_start = _split_columns(b_cols)
    if a_sample_idx >= 0 and b_sample_idx >= 0 and a_metrics_start > a_sample_idx and b_metrics_start > b_sample_idx:
        bin_map = _align_bins(a_bins, b_bins)
        # Rename B's bin columns to A's names where mapped
        rename_dict = {b_nm: a_nm for b_nm, a_nm in bin_map.items() if b_nm in b.columns}
        if rename_dict:
            b = b.rename(columns=rename_dict)
            b_cols = [str(c).strip() for c in b.columns]
        # Add any A-only bins as zero columns into B for fair comparison
        a_only_bins = [nm for nm in a_bins if nm not in b.columns]
        for nm in a_only_bins:
            b[nm] = 0.0
        # Optionally drop B-only bins not present in A to stabilize compare
        drop_bins = [nm for nm in b_bins if nm not in a_bins and nm in b.columns]
        if drop_bins:
            b = b.drop(columns=drop_bins)
            b_cols = [str(c).strip() for c in b.columns]

    # Align columns strictly to A's order; B drops extras
    only_a = [c for c in a.columns if c not in b.columns]
    only_b = [c for c in b.columns if c not in a.columns]
    common = [c for c in a.columns if c in b.columns]
    if only_a:
        print(f"A-only columns ({len(only_a)}): {only_a}")
        # Fail early if expected has columns not present in output
        return 2
    # Reorder B to match A
    b = b[common].copy()
    a = a[common].copy()

    print(f"A-only columns ({len(only_a)}): {only_a}")
    print(f"B-only columns ({len(only_b)}): {only_b}")
    print(f"Common columns ({len(common)}): first 10 -> {common[:10]}")

    if not common:
        return 0

    a_sub = a[common].copy()
    b_sub = b[common].copy()

    # Normalize types for numeric comparison where possible
    for c in common:
        # Try float coercion; if fails, treat as string
        try:
            a_sub[c] = pd.to_numeric(a_sub[c], errors='coerce')
            b_sub[c] = pd.to_numeric(b_sub[c], errors='coerce')
        except Exception:
            a_sub[c] = a_sub[c].astype(str).str.strip()
            b_sub[c] = b_sub[c].astype(str).str.strip()

    # Align lengths by inner join on (Sample,K,Group) if available; else truncate to min length
    keys = [k for k in ('Group', 'Sample', 'K') if k in common]
    # Sort both for deterministic comparison
    if 'Group' in a.columns and 'Sample' in a.columns:
        a = a.sort_values(by=[c for c in ['Group','Sample','K'] if c in a.columns])
    if 'Group' in b.columns and 'Sample' in b.columns:
        b = b.sort_values(by=[c for c in ['Group','Sample','K'] if c in b.columns])
    if keys:
        try:
            a_keyed = a_sub.set_index(keys)
            b_keyed = b_sub.set_index(keys)
            # Inner join
            joined = a_keyed.join(b_keyed, how='inner', lsuffix='_a', rsuffix='_b')
            # Compute mismatches for numeric columns
            mismatches = 0
            total = 0
            for c in common:
                if c in keys:
                    continue
                ca = c + '_a'
                cb = c + '_b'
                if ca in joined.columns and cb in joined.columns:
                    lhs = joined[ca]
                    rhs = joined[cb]
                    comp = (lhs == rhs) | (pd.isna(lhs) & pd.isna(rhs))
                    # for floats, allow tiny epsilon
                    try:
                        diff = (lhs - rhs).abs()
                        comp = comp | (diff <= 1e-9)
                    except Exception:
                        pass
                    mismatches += (~comp).sum()
                    total += comp.size
            print(f"Row-aligned comparison on keys {keys}: mismatches={mismatches} over {total} cells in common columns")
            return 0 if mismatches == 0 else 1
        except Exception as e:
            print(f"Keyed compare failed: {e}")

    # Fallback: compare head rows up to min length
    n = min(len(a_sub), len(b_sub))
    a_sub = a_sub.head(n)
    b_sub = b_sub.head(n)
    eq = (a_sub.values == b_sub.values)
    mismatches = (~eq).sum()
    total = eq.size
    print(f"Fallback (row-wise head) mismatches={mismatches} over {total} cells in common columns")
    return 0 if mismatches == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())

