# EntropyMax 2.0 – CI / CD (Working Plan)

Status: Not yet implemented. This document defines the pipeline we will adopt.

## Pipeline overview
```
PR / push
   │
   ├─ Lint & static analysis (C + Python)
   │
   ├─ Matrix build (Ubuntu / macOS / Windows)
   │    • build C backend (clang/gcc/MSVC)
   │    • run CTest (backend/tests)
   │
   ├─ Python tests
   │    • install dev reqs (requirements-dev.txt)
   │    • pytest (tests/python) incl. GUI smoke
   │
   ├─ (Optional) Build wheels (cibuildwheel)
   │    • manylinux / macOS / Windows
   │    • pytest on installed wheels
   │
   ├─ (Optional) Package GUI installers
   │    • PyInstaller (Win/mac), AppImage/.deb (Linux)
   │
   └─ Release artifacts (draft)
        • attach wheels/installers to GitHub Release
        • notifications on failure
```

## Jobs and tooling
| Stage | Tooling | Notes |
|------|---------|-------|
| Lint/static | clang-tidy, cppcheck; ruff, mypy | Fast feedback on style and types |
| Build C core | CMake + compiler matrix | Produces lib + `emx_cli`; run CTest |
| Python tests | pytest, pytest-qt | `tests/python`; GUI smoke guarded for headless |
| Wheels (opt) | cibuildwheel | Embed C library where appropriate |
| GUI packaging (opt) | PyInstaller, AppImage/fpm | End-user installers |
| Release | GitHub Actions + Releases | Draft release with artifacts |

## Triggers
| Trigger | Jobs |
|--------|------|
| Pull request to main | Lint, build, tests |
| Push to main | Lint, build, tests, (opt) wheels |
| Tag v* | Full pipeline incl. (opt) installers |

## Repository paths
- C: `backend/` (CTest configured in CMake)
- Python app: `src/app/`
- Standalone GUI: `frontend/`
- Tests: `tests/python/`
- Scripts: `scripts/`

## Configuration
- Dev tools are declared in `pyproject.toml` (ruff, mypy, pytest) and `requirements-dev.txt`.
- Cache directories to ignore: `.pytest_cache/`, `.mypy_cache/`, `**/__pycache__/`.

## Next steps
- Add `.github/workflows/ci.yml` implementing the above in stages.
- Add headless Qt configuration for GUI smoke tests in CI.
