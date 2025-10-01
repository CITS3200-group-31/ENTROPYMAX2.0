import os
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def convert(csv_path: str, parquet_path: str) -> None:
    df = pd.read_csv(csv_path)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, parquet_path)
    print(f"Wrote Parquet: {parquet_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 convert_output_to_parquet.py <input_csv> <output_parquet>")
        sys.exit(2)
    convert(sys.argv[1], sys.argv[2])


