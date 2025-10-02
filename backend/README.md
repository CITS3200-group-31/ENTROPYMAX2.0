# EntropyMax Backend (CSV-only)

This backend builds the EntropyMax runner and emits a processed CSV (`output.csv`) from two CSV inputs: a sample feature matrix and a GPS coordinates file.

## Prerequisites
- C/C++ toolchain
  - Windows: Visual Studio Build Tools 2022 (MSVC)
  - macOS: Xcode command line tools
  - Linux: gcc/g++ and make
- CMake (if using the CMake project under `backend/` directly)
- Optional: vcpkg + Apache Arrow/Parquet if you want Parquet support (disabled by default)

## Quick start (recommended)
Use the repository `Makefile` at the project root. By default it builds CSV-only.

```bash
# Build runner (CSV-only)
make runner

# Run with provided samples
./build/bin/run_entropymax data/raw/inputs/sample_group_1_input.csv \
  data/raw/gps/sample_group_1_coordinates.csv
# Output is written to ./output.csv
```

To enable optional Arrow/Parquet build path, set `ENABLE_ARROW=1` (requires dev libs):
```bash
make ENABLE_ARROW=1 runner
```

## Makefile targets
- `runner`: builds the backend runner at `build/bin/run_entropymax`
- `clean`: removes the local build directory
- `distclean`: alias for `clean`
- `setup`: installs Arrow/Parquet deps if possible and builds runner (Linux/macOS best effort)
- `deps`: runs `arrow-auto` and `pydeps`
- `arrow-auto`: attempts Arrow/Parquet installation via pkg manager or vcpkg
- `bootstrap-vcpkg`: clones and bootstraps `third_party/vcpkg`
- `frontend-deps`, `frontend-run`, `frontend-linux-setup`, `frontend-launch-linux`: convenience helpers for the Python UI

CSV-only is the default: the Makefile sets `ENABLE_ARROW ?= 0`. Override per-invocation:
```bash
make ENABLE_ARROW=1 runner
```

## Building with CMake (backend directory)
You can also use the CMake project in `backend/` (used on Windows/MSVC):
```bash
cd backend
cmake -S . -B build-vcpkg -DCMAKE_BUILD_TYPE=Release
cmake --build build-vcpkg --config Release -j 4
# Runner: backend/build-vcpkg/Release/run_entropymax.exe (on Windows)
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

- Output: `output.csv` in the project root
- Columns: `K,Group,Sample,<bins...>,% explained,Total inequality,Between region inequality,Total sum of squares,Within group sum of squares,Calinski-Harabasz pseudo-F statistic,latitude,longitude`

## Notes
- Whitespace trimming is applied to headers and tokens during CSV ingestion.
- The K sweep defaults to 2..20; override with environment variables or CLI flags.
- Preprocessing defaults: `row_proportions=0`, `em_gdtl_percent=1`. You may specify either `--row_proportions` or its synonym `--em_proportion`.
- Parquet output is intentionally disabled in this branch for simplicity. To restore Parquet, set `ENABLE_ARROW=1` and re-enable the Arrow path in `backend/CMakeLists.txt` and the conversion call in `backend/src/algo/run_entropymax.c`.
