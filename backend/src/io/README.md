### IO module (backend/src/io)

Compiled-only IO: C/C++ validation/merge and Arrow/Parquet read/write. No Python at runtime.

### Build/runtime dependencies
- Apache Arrow/Parquet C++ (installed via vcpkg; toolchain enabled in CMake)

### Key files
- `parquet_io.cc`:
  - Compiled postprocess: reads algorithm CSV output and GPS CSV, merges on `Sample`, and writes `data/parquet/output.parquet`.
  - Reorders columns to match frontend schema: `Group`, `Sample`, bins…, metrics…, `K`, `latitude`, `longitude`.
- `parquet_stub.c`: stubbed symbols when Arrow is unavailable (builds but returns non‑zero from writer).
- `verify_parquet.cc` (under `backend/tests/`): standalone verifier for schema and row parity.

### Orchestration
- `run_entropymax` (see `backend/src/algo/run_entropymax.c`) runs the algorithm and then calls the compiled writer to emit Parquet.
  - Inputs (fixed paths):
    - RAW CSV: `data/raw/sample_input.csv`
    - GPS CSV: `data/raw/sample_coordinates.csv`
  - Outputs:
    - CSV (parity/regression): `data/processed/sample_outputt.csv`
    - Parquet (frontend): `data/parquet/output.parquet`

### Parquet schema (frontend contract)
- Column order:
  1. `Group`
  2. `Sample`
  3..N-4: bin columns (doubles), then metrics columns (doubles) in the same order as CSV (excluding `K`)
  N-3: `K` (group count)
  N-2: `latitude` (double)
  N-1: `longitude` (double)

### Verification
- Build the verifier:
  - `cmake --build backend/build-vcpkg --target verify_parquet --config Release`
- Run:
  - `backend/build-vcpkg/Release/verify_parquet.exe`
- It asserts:
  - First two columns are `Group`, `Sample`
  - Tail is `[K, latitude, longitude]`
  - Column set parity vs CSV (ignoring the relocation of `K`)
  - Row counts match CSV

### Notes
- All legacy Python IO scripts have been removed. The C++ path is the single source of truth.
- Build artifacts and Parquet outputs are ignored in Git (`.gitignore` includes `backend/build-vcpkg/`, `build-vcpkg/`, and `*.parquet`).
