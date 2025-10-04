# EntropyMax Backend

This backend builds the EntropyMax runner and emits a processed CSV (`output.csv`) from two CSV inputs: a sample feature matrix and a GPS coordinates file.

## Prerequisites
- C/C++ toolchain
  - Windows: Visual Studio Build Tools 2022 (MSVC)
  - macOS: Xcode command line tools
  - Linux: gcc/g++ and make
- CMake (if using the CMake project under `backend/` directly)
- Optional: vcpkg + Apache Arrow/Parquet if you want Parquet support (disabled by default)

## Quick start (recommended)
Use the repository `Makefile` at the project root. It invokes CMake and writes outputs to `build/bin`.

```bash
# Build runner
make

# Run with provided samples (Windows example)
build\bin\run_entropymax.exe data\raw\inputs\sample_group_1_input.csv \
  data\raw\gps\sample_group_1_coordinates.csv
# Outputs are written under build context:
#  - CSV: backend/build-msvc/data/processed/csv/output.csv (dev run)
#  - Parquet: backend/build-msvc/data/processed/parquet/output.parquet (if Arrow deps present)
```

With Arrow/Parquet available (Windows via vcpkg auto-detection in CMake), the runner also writes Parquet.

## Makefile targets
- `make`: configure+build backend via CMake, stage exe to `build/bin`
- `make clean`: remove `backend/build-msvc`, `build/bin`, and `build/dlls`

CSV-only is the default: the Makefile sets `ENABLE_ARROW ?= 0`. Override per-invocation:
```bash
make ENABLE_ARROW=1 runner
```

## Building with CMake directly
You can also use the CMake project in `backend/` (used on Windows/MSVC):
```bash
cd backend
cmake -S . -B build-vcpkg -DCMAKE_BUILD_TYPE=Release
cmake --build build-vcpkg --config Release -j 4
# Runner: build/bin/run_entropymax.exe (Windows) or build/bin/run_entropymax
```

## Running the runner
CLI:
```bash
run_entropymax <sample_data_csv> <coordinate_data_csv> \
  [--EM_K_MIN N] [--EM_K_MAX N] [--EM_FORCE_K N] \
  [--row_proportions 0|1] [--em_proportion 0|1] [--em_gdtl_percent 0|1]
```
Example:
```bash
run_entropymax data/raw/inputs/sample_group_1_input.csv \
  data/raw/gps/sample_group_1_coordinates.csv --EM_K_MAX 15 --row_proportions 1 --em_gdtl_percent 1
```

- Output: `output.csv` under the build context; see console message for exact path
- Columns: `K,Group,Sample,<bins...>,% explained,Total inequality,Between region inequality,Total sum of squares,Within group sum of squares,Calinski-Harabasz pseudo-F statistic,latitude,longitude`

## Notes
- Whitespace trimming is applied to headers and tokens during CSV ingestion.
- The K sweep defaults to 2..20; override with environment variables or CLI flags.
- Preprocessing defaults: `row_proportions=0` (alias `em_proportion=0`), `em_gdtl_percent=1`.
- On Windows, if Parquet dependencies are missing, the runner prints each missing DLL and skips Parquet (no placeholder file).
