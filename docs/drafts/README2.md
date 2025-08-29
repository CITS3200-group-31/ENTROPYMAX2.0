# ENTROPYMAX 2.0 – Detailed Architecture (Superseded)

This draft has been superseded by `docs/ARCHITECTURE.md` (working copy). Please refer there for the current architecture. The content below remains for historical context.

## Proposed Repository Structure

```
ENTROPYMAX2/
├── legacy/                         # Read‑only VB6 artefacts for reference
├── src/
│   ├── c/                          # C11 core library (libentropymax)
│   │   ├── include/                # Public headers (stable C ABI)
│   │   ├── entropy/                # Source files
│   │   ├── tests/                  # C unit tests (e.g. Unity/CMocka)
│   │   └── CMakeLists.txt          # Cross‑platform build (macOS/Linux/Windows)
│   ├── python/
│   │   ├── entropymax/             # Python package
│   │   │   ├── core.py             # High‑level API
│   │   │   ├── _capi.pyi           # Type hints for the C API surface
│   │   │   ├── _cffi.py            # cffi bindings (default)
│   │   │   ├── _cython.pyx         # Cython bindings (optional accel)
│   │   │   ├── io.py               # CSV/pandas helpers
│   │   │   ├── vis.py              # Shared plotting helpers (Matplotlib/Plotly)
│   │   │   └── __init__.py
│   │   ├── pyproject.toml          # Build system (maturin/scikit‑build/cffi)
│   │   └── tests/                  # pytest + numpy test suite
│   └── gui/
│       ├── app/                    # PyQt6 application
│       │   ├── main.py             # Entrypoint
│       │   ├── widgets/            # Import wizard, results views
│       │   ├── views/              # Charts: CH & Rs vs k, group means, Z stats
│       │   └── resources/          # Icons, qss
│       └── pyproject.toml          # GUI packaging (optional)
├── examples/                       # Sample CSVs and walkthroughs
├── tests/                          # Cross‑layer tests/integration
├── docs/                           # Design docs & user guides
└── README2.md                      # This file
```

## C Core (libentropymax)

Public header sketch (`include/entropymax.h`):

```c
typedef struct {
  int32_t num_samples;     // jobs
  int32_t num_variables;   // nvar
  int32_t min_groups;      // default 2
  int32_t max_groups;      // default 20
  bool    row_proportions; // VB6 chkProp
  bool    grand_total_norm;// VB6 GDTLproportion
  bool    ch_permutations; // VB6 chkPerm
  int32_t ch_permutations_n; // default 100
  uint64_t rng_seed;       // determinism
} em_config_t;

typedef struct {
  double ch_value;     // Calinski–Harabasz
  double rs_percent;   // 100 * between / total inequality
  double sst_total;    // Prvsstt
  double sse_within;   // Prvsset
} em_k_metrics_t;

typedef struct {
  int32_t optimal_k;
  em_k_metrics_t *per_k;       // size (max_groups - min_groups + 1)
  int32_t *assignments;        // length num_samples; 1..k
  double  *group_means;        // [k * num_variables]
  double  *z_stats;            // [k * num_variables]
} em_result_t;

// API
int em_run(const em_config_t *cfg,
           const double *data,        // row‑major [num_samples * num_variables]
           const char *const *colnames, // optional
           const char *const *rownames, // optional
           em_result_t *out);

void em_free_result(em_result_t *res);
const char *em_version(void);
```

Notes:
- Numeric type: `double` throughout.
- Deterministic permutations via `rng_seed`.
- No temp files; everything in‑memory.
- Implementation mirrors VB6 logic: row proportions, grand‑total normalisation, total/between inequality with base‑2 logs, greedy re‑assignment loop, CH computation (with optional permutations).

## Python Package (entropymax)

- Primary I/O: NumPy arrays; optional pandas DataFrame helpers in `io.py` that enforce VB6 dialect by default (first row headers, first column sample IDs).
- Bindings:
  - Default: `cffi` (portable, easy to build wheels).
  - Optional: Cython path selected when available for speed; same public API.
- Public API example:

```python
from entropymax import run

result = run(
    data=df.iloc[:, 1:].to_numpy(float),
    rownames=df.iloc[:, 0].astype(str).tolist(),
    colnames=df.columns[1:].astype(str).tolist(),
    min_groups=2,
    max_groups=20,
    row_proportions=True,
    grand_total_norm=True,
    ch_permutations=True,
    ch_permutations_n=100,
    rng_seed=42,
)
```

Returns a dataclass with: `optimal_k`, `assignments`, `per_k` metrics, `group_means`, `z_stats`.

## GUI (PyQt6)

- Import wizard: CSV preview, dialect detection, column mapping, validation.
- Plots: CH and Rs vs k; table/heatmap of group mean proportions; Z‑statistics; copy/export.
- No Windows OCX dependencies; use Matplotlib/Plotly inside Qt.

## Open Questions (please confirm)

1) CSV dialect: separator, quoting, decimal point; confirm “header row + first column sample IDs”. Provide sample datasets.
2) Fidelity: exact replication vs numeric tolerance; preserve base‑2 logs and small‑variance guards?
3) Defaults: enable row proportions and grand‑total normalisation by default (as VB6 effectively does)?
4) Optimal k: choose by max CH; tie‑break by Rs or smallest k?
5) Permutations: keep feature; default n=100; fixed seed default?
6) Outputs: which artefacts to write by default (single consolidated CSV/JSON)?
7) Scale: expected samples × variables; need OpenMP parallelism?
8) Platforms: target macOS (arm64/x86_64), Windows, Linux; wheel distribution via PyPI?
9) Plotting: Matplotlib vs Plotly preference in the GUI?
10) R integration: reserve stable C ABI for future `reticulate`?

Once confirmed, we will populate headers, minimal C skeleton, Python stubs, and a GUI shell, and wire CI for wheels.



