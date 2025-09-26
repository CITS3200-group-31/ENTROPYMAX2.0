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
Responsibilities focus on repo hygiene, build verification, Python tooling, and CI enablement.

- Repository and build QA
  - Migrate/retire legacy Python IO scripts into `scripts/` and update `backend/src/io/README.md` accordingly.
  - Implement Makefile verification changes (schema inspection over CSV parity); maintain `legacy_parquet` target for historical conversions.
  - Ensure `.gitignore` excludes generated Parquet/CSV outputs; remove any tracked artifacts.
  - Deliverable: PR updating Makefile, scripts placement, `.gitignore`, and docs.
  - Acceptance: `make verify` runs runner and schema inspection with zero errors on CI.

- CI and quality gates
  - Add Python CI jobs: ruff/flake8, black --check; pin versions in `requirements-dev.txt`.
  - Set up headless PyQt smoke test job using xvfb; ensure it runs main window open/close and minimal flow.
  - Add pre-commit config for black, ruff, clang-format.
  - Deliverable: `.github/workflows/ci.yml` (or equivalent) with backend build/ctest and frontend lint/smoke jobs.
  - Acceptance: CI green on PRs to `main`.

- Data fixtures and tooling
  - Curate minimal test datasets under `tests/data/` (synthetic + edge cases: missing lat/lon, duplicate samples, constant bins).
  - Maintain `scripts/inspect_parquet.py`; add a schema linter to assert first two and last three columns and dtypes.
  - Deliverable: fixtures and updated scripts; README sections describing usage.
  - Acceptance: integration tests consume fixtures and pass in CI.

### Noah
Responsibilities center on backend numerical correctness, determinism, and performance.

- Backend unit and property tests
  - Implement unit tests for `preprocess.c` (row/col normalization, means/SD guardrails) and `metrics.c` (total inequality, CH; tolerance specs).
  - Add property-based tests for CH and inequality invariants (duplication monotonicity; invariance under bin reordering) with deterministic RNG.
  - Ensure RNG seeding is configurable via API/env; document determinism guarantees in tests.
  - Deliverable: tests under `backend/tests/` and CTest registration.
  - Acceptance: `ctest --output-on-failure` passes locally and in CI with -O2 and ASan builds.

- Integration and performance
  - Add CTest integration case invoking `run_entropymax` on tiny fixture; validate schema and row count via C++ checker.
  - Introduce AddressSanitizer build target and run key unit tests under ASan in CI.
  - Define performance budget on a medium dataset; capture baseline; fail CI on >20% regressions.
  - Deliverable: CMake/CTest updates, ASan job, performance script and thresholds.
  - Acceptance: CI shows green for normal build and ASan; performance job stable across PRs.

### Jeremy
Responsibilities emphasize frontend reliability, UX verification, and end-to-end flows.

- Frontend tests and harness
  - Build pytest + pytest-qt harness; component tests for `InteractiveMapWidget` (selection, zoom, markers), `ChartWidget` (series + optimal marker), `SettingsDialog` (apply/cancel), `GroupDetailPopup` (lines + signal emits).
  - Implement headless integration test: simulate selecting input/GPS, Generate Map, Run Analysis; wait for Parquet; assert charts populated and optimal K highlighted; verify sample list interactions.
  - Deliverable: tests under `frontend/tests/` with fixtures and CI execution support (xvfb).
  - Acceptance: tests pass locally and on CI; flaky tests are quarantined with retries.

- Docs and UX QA
  - Keep `frontend/README.md` current; document export and help flows; ensure test coverage for these interactions.
  - Add lightweight visual regression: capture PNGs of charts/map and compare image hashes with tolerances.
  - Deliverable: updated docs, test utilities for screenshots.
  - Acceptance: doc links valid; visual regression job stable and non-flaky.

## 7) Exit criteria
- All unit and integration tests green in CI.
- No -Wall/-Wextra warnings in backend builds.
- Parquet schema verified and stable.
- Frontend smoke passes headless on CI; primary interactions validated.


