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
- Ben
  - Migrate/retire legacy Python IO scripts (move to `scripts/`, update docs).
  - Implement Makefile cleanup; replace CSV parity with Parquet schema checks.
  - Add CI jobs for Python (ruff/flake8, black) and PyQt smoke test.
- Noah
  - Backend unit tests for preprocess/metrics; define numeric tolerances.
  - Property-based and regression tests for CH/inequality; seed determinism.
  - Wire CTest in CI; AddressSanitizer build job; performance budget test.
- Jeremy
  - Frontend test harness (pytest-qt); component tests for map, charts, settings, popups.
  - Integration test: headless run of main workflow including Parquet wait and chart assertions.
  - Update frontend README to current components; cover export/help flows.

## 7) Exit criteria
- All unit and integration tests green in CI.
- No -Wall/-Wextra warnings in backend builds.
- Parquet schema verified and stable.
- Frontend smoke passes headless on CI; primary interactions validated.


