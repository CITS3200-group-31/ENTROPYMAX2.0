### IO module (backend/src/io)

Overview of CSV validation, CSV→Parquet conversion, and Parquet merge utilities. Python scripts are the source of truth; C files are thin shims that invoke them.

### Dependencies
- Python 3.x
- pandas, pyarrow (for Parquet)

### Files
- `convert_csv_to_parquet.py`: CSV → Parquet. Lowercases/strips column names.
- `validate_csv_raw.py`: Validates RAW CSV:
  - First column exactly `Sample Name`
  - Remaining headers numeric, strictly ascending
  - `Sample Name` non-empty; data columns numeric and non-null
- `validate_csv_gps.py`: Validates GPS CSV:
  - Exact columns (order-sensitive): `Sample`, `Latitude`, `Longitude`
  - `Sample` non-null; `Latitude`/`Longitude` numeric and within valid ranges
- `run_converter.py`: Orchestrates validation (RAW + GPS CSV) and converts the GPS CSV to Parquet.
- `run_combine.py`: Merges Parquet files on `sample`; expects columns:
  - Main parquet: `sample`
  - GPS parquet: `sample`, `latitude`, `longitude`
- `run_converter_execute.c` / `run_combine_execute.c`: C entrypoints that exec the Python scripts via `python3`.
- `csv_stub.c` / `parquet_stub.c`: Stubs (return -1). Not implemented.

### Typical workflows
- Validate and convert GPS CSV after validating both inputs:
```bash
python3 run_converter.py <raw_data.csv> <gps.csv>
# Produces: <gps.parquet> adjacent to gps.csv
```

- Combine Parquet files by `sample`:
```bash
python3 run_combine.py <main.parquet> <gps.parquet> <output.parquet>
```

### Notes
- Column casing: `convert_csv_to_parquet.py` lowercases column names. GPS CSV validation happens before conversion; resulting Parquet columns are lowercase and match `run_combine.py` expectations.
- CLI help strings: `run_combine.py` usage text mentions a different filename; the actual script name is `run_combine.py`.
- C shims assume `python3` is on PATH.

### Minimal examples
```bash
# Validate RAW
python3 -c "from validate_csv_raw import validate_csv_structure as v; v('data/raw/sample_input.csv'); print('ok')"

# Validate GPS
python3 -c "from validate_csv_gps import validate_csv_gps_structure as v; v('data/raw/sample_coordinates.csv'); print('ok')"

# Convert CSV → Parquet
python3 -c "from convert_csv_to_parquet import convert_csv_to_parquet as c; c('data/raw/sample_coordinates.csv','data/parquet/coords.parquet')"

# Combine Parquet
python3 run_combine.py data/processed/sample_output.parquet data/parquet/coords.parquet data/parquet/combined.parquet
```


