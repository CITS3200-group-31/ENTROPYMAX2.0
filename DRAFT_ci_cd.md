# EntropyMax 2.0 – CI / CD Pipeline

## Pipeline snapshot
```
             PR / push
                    │
     Lint & static analysis (C + Python)
                    │
    Matrix build (Ubuntu / macOS / Windows)
        • compile libentropymax (gcc / clang / MSVC)
        • run Unity tests + coverage
                    │
     Build Python wheels (cibuildwheel)
        • manylinux / macOS / Windows wheels
        • pytest on installed wheel
                    │
     Package GUI installers
        • PyInstaller   (exe / dmg)
        • AppImage or .deb (Linux)
                    │
     Sign & upload artefacts
        • code‑sign installers
        • draft GitHub Release (wheels + installers)
        • optional push wheels to PyPI
                    │
         Slack / e‑mail alerts on failure
```

## Stage details

| Stage | Tooling | Outcome |
|-------|---------|---------|
| **Lint + static** | `clang‑tidy`, `cppcheck`; `ruff`, `mypy` | Fast feedback, code cleanliness |
| **Build C core** | GCC, Clang, MSVC in GitHub Actions matrix | Shared library + Unity tests |
| **Wheel build** | `cibuildwheel` | `.whl` files with embedded C DLL/SO/DYLIB |
| **GUI packaging** | PyInstaller (Win/mac), AppImage/`fpm` (Linux) | End‑user installers |
| **Signing & release** | Signtool / codesign + GitHub Release API | Draft release, artefacts attached |
| **Notifications** | GitHub Actions → Slack / e‑mail | Immediate failure alerts |

## Repository layout
```
entropymax/
    src/                ← C core
    bindings/           ← Cython / cffi
    gui/                ← PyQt frontend
    cli.py              ← batch runner
tests/
    python/             ← pytest
    c/                  ← Unity
.github/workflows/      ← CI YAML files
```

## Branch & trigger policy
| Trigger | Jobs run |
|---------|----------|
| **Pull request** to `develop` | Lint, build, unit tests, wheels (no installers) |
| **Merge** to `main` / version tag | Full pipeline inc. installers & signing |
| **Nightly cron** | Re‑run tests on latest deps |

