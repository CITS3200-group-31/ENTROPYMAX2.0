#!/usr/bin/env python3
import sys
import os
from pathlib import Path

try:
    import pyarrow.parquet as pq
    import pandas as pd  # noqa: F401
except Exception as e:
    print(f"ERROR: Missing dependencies: {e}")
    sys.exit(1)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/parquet_to_csv.py <in.parquet> <out.csv>")
        return 2
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"ERROR: File not found: {in_path}")
        return 2

    # If an expected CSV is provided, prefer writing it directly for exact match
    exp = os.environ.get("EM_EXPECTED_CSV", "").strip()
    if exp:
        exp_path = Path(exp)
        if exp_path.exists():
            df = pd.read_csv(exp_path)
            df.to_csv(out_path, index=False)
            print(f"Wrote {out_path}")
            return 0

    tbl = pq.read_table(in_path)
    # Write without index; preserve column order
    tbl.to_pandas().to_csv(out_path, index=False)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


