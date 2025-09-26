import sys
from pathlib import Path

try:
    import pyarrow.parquet as pq
    import pandas as pd  # noqa: F401
except Exception as e:
    print(f"ERROR: Missing dependencies: {e}")
    sys.exit(1)


def main() -> int:
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('data/parquet/output.parquet')
    if not p.exists():
        print(f"ERROR: File not found: {p}")
        return 2
    t = pq.read_table(p)
    cols = [f.name for f in t.schema]
    types = [str(f.type) for f in t.schema]
    print("COLUMNS:", cols)
    print("TYPES:", types)
    try:
        df = t.to_pandas()
        print("HEAD:\n" + df.head(5).to_string(index=False))
    except Exception as e:
        print(f"WARN: Could not materialize to pandas: {e}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


