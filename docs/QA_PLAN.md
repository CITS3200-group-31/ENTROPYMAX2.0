# Testing and QA Strategy for ENTROPYMAX 2.0

## 1) Scope and goals
- Backend: deterministic, correct CSV→metrics→Parquet pipeline; schema contract; performance within target bounds.
- Frontend: stable PyQt UI behavior; correct loading of Parquet; consistent visualization and interactions.

## 2) Backend tests
- Unit tests (C/CTest)
  - preprocess: row/column normalization; means/SD edge cases.
  - metrics: total inequality, CH; precision tolerances; deterministic RNG with fixed seed.
  - grouping: initial assignment, RS stat, between-inequality; k-sweep boundaries.
- Integration tests
  - Small synthetic CSV + GPS → run `run_entropymax` → validate Parquet schema:
    - Columns start with Group, Sample; tail [K, latitude, longitude].
    - Row count equals CSV rows; aggregates validated within tolerance.
  - Golden regression
    - For fixed input, snapshot Parquet columns and key aggregates; compare within tolerances.
- Property-based tests
  - Monotonicity checks on CH for duplicated rows; invariance under bin column reordering.
- Performance tests
  - Time budget on medium dataset; memory cap; fail on regressions beyond threshold.
- Static checks
  - clang-tidy/clang-format; -Wall -Wextra clean build; AddressSanitizer job for unit tests.

## 3) Frontend tests
- Unit/component tests (pytest + pytest-qt)
  - InteractiveMapWidget: selection, zoom_to_location, render markers; signal emissions.
  - ChartWidget: plot series and optimal marker rendering.
  - SettingsDialog & VisualizationSettings: defaults, apply/cancel flows.
  - GroupDetailPopup: loads expected lines; emits click signals.
- Integration (headless)
  - Launch main window; simulate loading input and GPS; Generate Map; assert map/list populated.
  - Run Analysis with tiny dataset; wait for Parquet; assert charts populated, optimal K marker placed.
- End-to-end smoke
  - Raw CSV/GPS → Parquet → UI render; run in CI with xvfb.
- Lint/format
  - ruff/flake8, black; mypy on utils where feasible.
- Visual regression (optional)
  - Capture PNG snapshots of charts/map and compare image hashes/tolerances.

## 4) Test data strategy
- Minimal synthetic datasets under `tests/data/`:
  - 5–10 rows CSV + matching GPS.
  - Edge cases: missing lat/lon, duplicate sample names, constant bins.

## 5) CI matrix
- Linux (primary), macOS optional.
- Jobs:
  - Backend: CMake build, `ctest --output-on-failure`, AddressSanitizer job.
  - Frontend: ruff/flake8, black --check, pytest-qt headless smoke.
- Artifacts: test logs and sample Parquet from integration tests (not committed).

## 6) Task ownership and allocation
### Ben
- Repository and build QA
  - Migrate/retire legacy Python IO scripts into `scripts/` and update `backend/src/io/README.md` accordingly.
  - Implement Makefile verification changes (schema inspection over CSV parity); maintain `legacy_parquet` target for historical conversions.
  - Add Python CI jobs (ruff/flake8, black --check) and headless PyQt smoke (xvfb).
- Data fixtures and tooling
  - Curate minimal test datasets under `tests/data/` (synthetic + edge cases).
  - Maintain `scripts/inspect_parquet.py` and add a simple Parquet schema linter used by CI.

### Noah
- Backend unit and property tests
  - Implement unit tests for `preprocess.c` and `metrics.c`; define numeric tolerances for floating-point comparisons.
  - Add property-based tests for CH/inequality invariants (e.g., duplication monotonicity) using deterministic seeds.
  - Ensure deterministic RNG seeding is exposed/configurable; document expected determinism in tests.
- Integration and performance
  - Add CTest integration test invoking `run_entropymax` on tiny fixture; validate Parquet schema and counts.
  - Add AddressSanitizer job and a performance budget test on a medium dataset; set thresholds and fail on regressions.

### Jeremy
- Frontend tests and harness
  - Build pytest + pytest-qt harness; write component tests for `InteractiveMapWidget`, `ChartWidget`, `SettingsDialog`, and `GroupDetailPopup` (signals, state, rendering).
  - Implement headless integration test: load CSV/GPS, Generate Map, Run Analysis, wait for Parquet, assert charts populated and optimal K marker placed.
- Docs and UX QA
  - Update `frontend/README.md` where component names/flows change; ensure help dialogs and export flow are documented and tested.
  - Optional lightweight visual regression: capture PNG snapshots of charts/map and compare using image hash tolerances.

## 7) Exit criteria
- All unit and integration tests green in CI.
- No -Wall/-Wextra warnings in backend builds.
- Parquet schema verified and stable.
- Frontend smoke passes headless on CI; primary interactions validated.


