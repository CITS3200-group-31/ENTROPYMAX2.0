# Backend overview (C library and CLI)

This document describes the modular C backend in `backend/`: what each part does, how to build it, and how to use the command‑line tool in a CSV → raw Parquet → processed Parquet pipeline.

## Layout

```
backend/
├─ CMakeLists.txt                  # Builds static lib `entropymax` and CLI `emx_cli`
├─ include/                        # Public headers (stable C ABI)
│  ├─ backend.h                    # High‑level config types and future convenience API
│  ├─ preprocess.h                 # Row/grand‑total normalisation; means/SD
│  ├─ metrics.h                    # Total inequality; CH; Z statistics
│  ├─ grouping.h                   # Initial groups; between‑inequality; Rs; optimiser
│  ├─ sweep.h                      # k‑sweep orchestration and per‑k metrics
│  ├─ csv.h                        # CSV reader table representation / API
│  ├─ parquet.h                    # Parquet writer API
│  └─ util.h                       # Allocation helpers
├─ src/
│  ├─ algo/
│  │  ├─ backend_algo.c           # Entrypoint glue (preprocess → sweep → write)
│  │  ├─ preprocess.c             # Noah: transforms and base stats
│  │  ├─ metrics.c                # Noah: total inequality, CH, Z
│  │  ├─ grouping.c               # Will: grouping engine & optimiser
│  │  └─ sweep.c                  # Will: k‑sweep orchestration
│  ├─ io/
│  │  ├─ csv_reader.c             # CSV → in‑memory table (placeholder)
│  │  └─ parquet_writer.c         # Table → Parquet (placeholder; writes processed Parquet)
│  ├─ util/
│  │  └─ util.c                   # Tiny alloc wrappers
│  └─ cli/
│     └─ emx_cli.c                # CLI: reads CSV, runs algorithm, writes Parquet
└─ tests/
   └─ test_backend.c              # C tests (add cases as implementation lands)
```

## Responsibilities

- `include/backend.h`
  - Defines `em_config_t` (run configuration) and a future convenience API `em_run_from_csv(...)`.
  - Keep types ABI‑stable; favour POD structs, explicit sizes, and error codes.

- `include/algo.h` / `src/algo/backend_algo.c`
  - Algorithm entrypoint `em_run_algo(...)` receives a dense, row‑major numeric matrix with optional row/column names and an output Parquet path for processed Parquet.
  - Today it forwards directly to the Parquet writer; the entropy/classification logic will be implemented here next.

- `include/csv.h` / `src/io/csv_reader.c`
  - Loads a CSV into a `csv_table_t` (SoA‑ish bundle: `double* data`, `char** colnames`, `char** rownames`, `rows`, `cols`). Used by the CSV→raw Parquet converter.
  - Placeholder returns an error until implemented.
  - Target dialect: first row header, first column sample IDs, comma separator. This will be made configurable later.

- `include/parquet.h` / `src/io/parquet_writer.c`
  - Writes processed results to Parquet (Arrow/Parquet C API planned).
  - Placeholder returns an error until implemented. During early prototyping we may route Parquet I/O via the Python layer.

- `src/cli/emx_cli.c`
  - Minimal CLI that wires CSV → algorithm → Parquet. Intended for batch usage and CI.

- `src/util/util.c` / `include/util.h`
  - Small allocation helpers, kept trivial for now.

## Build

Requirements:
- CMake ≥ 3.16
- A C11 compiler (clang/gcc/msvc)

Commands:
```bash
cmake -S backend -B backend/build
cmake --build backend/build --config Release
```

Outputs:
- Static library: `backend/build/libentropymax.*`
- CLI executable: `backend/build/emx_cli` (intended: accepts raw Parquet, writes processed Parquet)

Run tests (via CTest):
```bash
cd backend/build
ctest --output-on-failure
```

## CLI usage

```bash
# Planned usage (subject to CLI finalisation):
# 1) csv_to_parquet: CSV → raw.parquet
# 2) emx_cli: raw.parquet → processed.parquet

backend/build/emx_cli raw.parquet processed.parquet
```
- Exits with non‑zero on error (currently, CSV/Parquet are unimplemented placeholders, so it will error until those are filled in).

## C APIs (current state)

- High‑level config (future convenience call):
```c
// backend/include/backend.h
typedef struct {
  int32_t num_samples;
  int32_t num_variables;
  bool row_proportions;
  bool grand_total_norm;
  bool ch_permutations;
  int32_t ch_permutations_n;
  uint64_t rng_seed;
} em_config_t;

int em_run_from_csv(const char *csv_path,
                    const char *parquet_out_path,
                    const em_config_t *cfg);
```

- Algorithm entrypoint (array → Parquet):
```c
// backend/include/algo.h
int em_run_algo(const double *data,
                int32_t rows,
                int32_t cols,
                const char *const *colnames,
                const char *const *rownames,
                const char *parquet_out_path);
```

- CSV table representation:
```c
// backend/include/csv.h
typedef struct {
  double *data;      // row‑major [rows * cols]
  char **colnames;   // size cols
  char **rownames;   // size rows
  int32_t rows;
  int32_t cols;
} csv_table_t;

int csv_read_table(const char *path, csv_table_t *out);
void csv_free_table(csv_table_t *t);
```

## Roadmap (backend)
- Implement CSV parsing (libcsv/Arrow CSV or a small internal reader).
- Implement Parquet writing (Apache Arrow C/GLib APIs), with a short‑term Python‑mediated fallback if needed.
- Port the VB6 entropy/classification routine into `src/algo/backend_algo.c` using `double` precision and the config in `em_config_t`.
- Add unit tests in `backend/tests/` and wire them in CTest (already configured).

## Notes
- The C library is designed for a stable ABI so Python bindings (cffi, if we decide to use it) can link without churn.
- No temp files are used; data flows in‑memory from CSV to Parquet.
- Error handling is via integer return codes (0 success, non‑zero error); an error enum will be added when CSV/Parquet are implemented.


