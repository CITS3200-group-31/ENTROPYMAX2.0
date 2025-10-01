# EntropyMax 2.0 – Architecture (Working Copy)

## Overview
EntropyMax 2.0 separates compute-heavy C code from a Python GUI/frontend. Current code implements the structure with placeholders for CSV/Parquet I/O.

```
CSV(gps) + CSV(raw) ─▶ merge ─▶ raw Parquet ─▶ C backend (libentropymax) ─▶ processed Parquet ─▶ Python GUI (PyQt6)

During the porting phase, a developer CSV runner (`run_entropymax`) is used to generate a consolidated CSV with per‑k grouped outputs for verification.
```

- C backend (`backend/`): static library + CLI scaffold; headers under `backend/include/`. A developer runner writes a consolidated CSV: K,Group,Sample,<bins>, and per‑row metrics (% explained, Total/Between, SST/SSE, CH).
- Python app shell (`src/app`): prototype entrypoint with GUI structure and bindings placeholders.
- Standalone frontend (`frontend/`): PyQt6 application with widgets, sample data, and tests.
- Tests (`tests/python`): pytest smoke and unit tests for Python layers.

## Repository map (current)
```
ENTROPYMAX2/
├── backend/                 # C11 backend (CMake)
│   ├── include/             # headers: algo.h, backend.h, csv.h, parquet.h, ...
│   ├── src/
│   │   ├── algo/            # backend_algo.c, preprocess.c, metrics.c, grouping.c, sweep.c
│   │   ├── io/              # csv_reader.c, parquet_writer.c (placeholders)
│   │   ├── util/            # util.c
│   │   └── cli/             # emx_cli.c
│   └── tests/               # C tests wired via CTest
├── src/app/                 # Python prototype app package
│   ├── bindings/            # cffi/cython stubs and loader
│   ├── core/                # datastore/io helpers
│   └── gui/                 # main_window, map/plot views, assets
├── frontend/                # Standalone PyQt6 GUI (recommended for UI dev)
│   ├── components/          # Control panel, map widget, charts, etc.
│   ├── utils/               # csv export helpers
│   ├── main.py              # GUI entrypoint
│   └── requirements.txt     # GUI deps (PyQt6, WebEngine, pyqtgraph, folium, pyarrow)
├── tests/python/            # pytest, includes GUI smoke test
├── scripts/                 # build/run helper scripts
└── docs/                    # working documentation (this file, porting guide, etc.)
```

## Data flow (intended)
1. Convert two inputs to a single raw Parquet:
   - GPS CSV (lat, lon, sample_id, optional attrs)
   - Raw data CSV (sample_id, variables...)
   - Merge on sample_id to produce one raw Parquet (identifiers, variables, GPS metadata).
2. Backend reads raw Parquet, runs preprocess → metrics → grouping → sweep in `backend/src/algo/` using `double`.
3. Backend writes processed Parquet (schema: per‑k metrics, optimal k, assignments, group stats).
4. Python GUI loads processed Parquet to render plots/maps and support exports.

CSV/Parquet steps are placeholders pending implementation; GUI currently uses sample data.

## Build & run summary
- Backend build: `./scripts/build_backend.sh` → outputs library and `emx_cli`.
- Frontend run: `cd frontend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py`.
- Prototype app: `python -m app` from repo root.

## Interfaces and stability
- C headers under `backend/include/` define public API surface; prefer POD structs and explicit sizes.
- Python bindings (`src/app/bindings`) locate and load the compiled C library (stubs present).

## Current limitations
- CSV→Parquet conversion and Parquet read/write are not yet implemented; CLI will return an error until those land.
- GUI runs with sample data; backend integration wiring is pending.

## Next steps (implementation)
- Implement CSV parsing and Parquet writing (short-term: Python fallback acceptable).
- Port core VB6 routines into `preprocess.c`, `metrics.c`, `grouping.c`, `sweep.c` with tests.
- Expose a minimal stable C API for Python; connect GUI actions to backend results.
