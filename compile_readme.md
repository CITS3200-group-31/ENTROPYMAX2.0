# Build and verify (cross‑platform)

This project ships a cross‑platform Makefile that builds the backend library and the developer runner, then verifies the CSV output against a known‑good baseline.

Quick start (macOS, Linux, Windows/MSYS):

```
make
```

What it does:
- Builds the static library: build-make/lib/libentropymax.a
- Builds the runner: build-make/bin/run_entropymax
- Runs the runner to generate data/processed/sample_outputt.csv
- Diffs the generated CSV against data/processed/sample_output_CORRECT.csv

Notes:
- Override compiler with `CC=clang` or `CC=gcc` if desired, e.g.: `make CC=clang`
- Tools target (optional CLI): `make tools`
- Clean builds: `make clean` (remove build-make/)
- Full clean: `make distclean`

If the verify step passes, you’ll see “Baseline match OK”.
