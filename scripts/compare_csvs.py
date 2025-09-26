#!/usr/bin/env python3
import sys
import pandas as pd


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

    common = [c for c in a_cols if c in b_cols]
    only_a = [c for c in a_cols if c not in b_cols]
    only_b = [c for c in b_cols if c not in a_cols]

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
    keys = [k for k in ('Sample', 'K', 'Group') if k in common]
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
            return 0
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
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

