import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def convert_csv_to_parquet(csv_path, parquet_path):
    # Read CSV and normalize headers
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # Drop unnamed/blank spill columns from trailing commas
    keep = [c for c in df.columns if c and not c.startswith('unnamed:')]
    if len(keep) != len(df.columns):
        df = df.loc[:, keep]

    # For numeric matrix inputs, allow NaNs and fill with 0 for stability
    # (Downstream algo treats missing as 0 when proportionalizing.)
    df = df.fillna(0)

    table = pa.Table.from_pandas(df)
    pq.write_table(table, parquet_path)
