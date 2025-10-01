### Data layout (data/)

This directory holds all inputs/outputs exchanged with the client and the backend in a consistent, documented structure. The backend now emits Parquet matching the frontend’s schema; legacy CSVs can be converted with a helper script.

### Directory structure

- raw/
  - inputs/: client-provided raw bin CSVs (headers: `Sample Name`, numeric bins ascending)
  - gps/: client-provided GPS CSVs (headers: `Sample` or `Sample Name`, `Latitude`, `Longitude`)
  - legacy_outputs/: client-provided legacy EntropyMax CSV outputs (original VB6/legacy layout)

- parquet/
  - raw/: pre‑algorithm Parquet (e.g., merged inputs if needed)
  - processed/: post‑algorithm Parquet (frontend‑ready). The backend writes `data/parquet/output.parquet`.

- processed/
  - csv/: legacy/dev CSV outputs if generated for parity/regression (not required for frontend)

All other files under data/ should be considered transient artifacts.

### File naming conventions
- Raw inputs
  - `raw/inputs/<dataset>_raw.csv`
  - `raw/gps/<dataset>_gps.csv`
- Legacy outputs
  - `raw/legacy_outputs/<dataset>_legacy_output.csv`
- Parquet
  - `data/parquet/raw/<dataset>_merged_input.parquet` (optional)
  - `data/parquet/output.parquet` (current backend default)

### Frontend schema contract (processed Parquet)
- Column order must be:
  1. `Group`
  2. `Sample`
  3..N-4: bin columns (doubles), then metrics (doubles) in the same order as the backend CSV (excluding `K`)
  N-3: `K` (group count)
  N-2: `latitude` (double)
  N-1: `longitude` (double)

### Converting legacy CSV outputs

Use the helper script to convert old legacy output CSVs into the new column structure (and optionally add latitude/longitude if provided):

```bash
python scripts/convert_legacy_output.py \
  --legacy raw/legacy_outputs/<dataset>_legacy_output.csv \
  --out processed/csv/<dataset>_converted.csv \
  [--gps raw/gps/<dataset>_gps.csv]
```

Behavior:
- Reorders columns to `Group, Sample, bins…, metrics…, K` (moves `K` to third‑from‑last if GPS is provided, otherwise to last).
- If `--gps` is provided, merges `latitude`/`longitude` by `Sample` and appends them as the last two columns.
- Preserves all numeric values and header names as-is.

### Notes
- The backend’s compiled code writes `data/parquet/output.parquet`. For reproducible runs, clear `data/parquet/` before re‑execution if needed.
- All Parquet and build artifacts are ignored by Git; the structure and this README are kept.


