# Legacy VB6 audit – what to port and what to drop

This document catalogues the VB6 code under `legacy/`, identifies the calculation routines we must port verbatim (semantics‑preserving) to C, and flags UI/packaging code that is out of scope.

## Inventory

- `legacy/src/EntropyMax.vbp`
  - VB6 project file; lists forms, OCX dependencies (`MSCHRT20.OCX`, `comdlg32.ocx`). Packaging metadata. Not ported.
- `legacy/src/EntropyMax.vbw`
  - VB6 workspace/layout. Not ported.
- `legacy/src/frmSplash.frm` (+ `.frx`)
  - Splash screen only (timer, on‑top window). Not ported.
- `legacy/src/Module1.bas`
  - Types and globals:
    - `GroupData`, `GroupSetData` – group count, group means, member IDs.
    - `GetSaveFile` – Windows common dialog for open/save (UI). Not ported.
    - `SetCursorPos`/`POINTAPI` – Windows API glue. Not ported.
- `legacy/src/Form1.frm` (+ `.frx`)
  - Main form UI layout (menus, buttons, MSChart). Contains the bulk of the algorithm as form code.
  - Calculation and control‑flow routines to port (see below).
- `legacy/package/**`
  - VB6 Packaging wizard artefacts: CAB files, `SETUP.LST`, `Project1.DDF`, `Setup.Lst`, `EntropyMax.exe`. Not ported.

## Routines to port (calculation only)

Port these with behaviour preserved, using `double` precision in C and base‑2 logarithms as in VB6.

- Data transforms
  - `Proportion(…)`: per‑row normalisation to proportions when enabled.
  - `GDTLproportion(…)`: grand‑total normalisation to percentages.
  - `MeansSTdev(…)`: column means and standard deviations; treat tiny negative variance (>-1e‑4) as zero.
- Inequality metrics
  - `TOTALinequality(…)`: compute total inequality `tineq` and column totals `Y()` using log2.
  - `BETWEENinquality(…)`: compute between‑group inequality for current assignments.
  - `RSstatistic(…)`: percentage explained: `pineq = bineq / tineq * 100` with edge cases.
- Grouping search
  - `INITIALgroup(…)`: equal‑sized initial grouping.
  - `SWITCHgroup(…)`: greedy reassignment loop over samples × groups; calls `BETWEENinquality`, `RSstatistic`, `OPTIMALgroup`.
  - `OPTIMALgroup(…)`: accept/reject reassignments; recompute group means (`sumx / ngrp`).
  - `LOOPgroupsize(…)`: sweep group counts from min to max; manage per‑k metrics and choose optimum.
- Statistics and reporting (numerics only)
  - `CHTest(…)`: Calinski–Harabasz pseudo‑F; optional permutations (default 100); deterministic seed policy to be added.
  - `RITE(…)`: compute per‑group Z statistics from group means, overall means, and SD; exclude file I/O.

Notes
- Keep arrays as dense row‑major matrices in C: `double result[jobs][nvar]` flattened.
- Preserve base‑2 logarithms and zero‑guards to match legacy outputs.
- Remove all file/GUI I/O from these routines; pass inputs/outputs via memory.

## Out of scope / to drop

- UI and Windows specifics: forms, menus, `MSCHRT20.OCX`, `comdlg32.ocx`, `HtmlHelp`, `SetCursorPos`, message boxes.
- File dialogs and any VB file paths (e.g. temp `c:\\column`).
- Charting and clipboard code.
- Packaging artefacts under `legacy/package/**`.
- All printing to `#1/#2/#3` log/output files and chart updates in `SAVEdata`/`RITE`.

## File I/O behaviour (for reference)

- `FileK3(…)` reads CSV, writes a temp `c:\\column` to infer `nvar`, then reloads data and titles.
  - In the modern system we will eliminate temp files and parse in one pass.
  - CSV dialect implied: first row headers (nvar+1 with leading row title), first column sample IDs, remaining are numeric variables.

## Proposed C mapping (backend)

- `src/algo/backend_algo.c`
  - Implement: `Proportion`, `GDTLproportion`, `MeansSTdev`, `TOTALinequality`, `BETWEENinquality`, `RSstatistic`, `INITIALgroup`, `SWITCHgroup`, `OPTIMALgroup`, sweep over k (formerly `LOOPgroupsize`), `CHTest`, Z‑stats.
- `src/io/csv_reader.c`
  - Replace `FileK3`: parse CSV directly to `csv_table_t` (headers + data) with no temp files.
- `src/io/parquet_writer.c`
  - Replace `SAVEdata` file outputs with a Parquet writer over in‑memory results.

## Edge cases to preserve

- Variance guard in `MeansSTdev`: if `(SD/N) - mean^2` is slightly negative in [-1e‑4, 0), set SD to 0.
- Logarithms: base‑2; skip terms when values are zero.
- `RSstatistic`: if `tineq == 0` and `bineq == 0`, set `pineq = 100` and mark `ixout = 1`.
- Group initialisation: final remainder assigned to last group (VB6 behaviour).

## To be confirmed

- Default min/max groups (VB6 uses 2..20 when `chkGrps` set). Adopt 2..20 as default?
- Permutations default `n=100` with deterministic RNG seed.
- Tie‑break strategy for optimal k (max CH; if tie, lowest k?).

Once confirmed, we will mirror these routines in C, add unit tests that diff outputs against known VB6 runs, and wire them to the Python wrapper and GUI.


