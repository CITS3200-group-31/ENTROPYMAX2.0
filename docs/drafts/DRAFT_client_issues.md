# Client Issues & Feature Requests (Working list)

This list captures client‑facing requests. For triage and status, see GitHub Issues. Items here should reflect actual project scope and be kept in sync with the issue tracker.

## Proposed Features for EntropyMax 2.0

### 1. Automated Grain-Size Grouping & Curves

Replace manual Excel work: program must ingest a CSV, run the 2-to-20-group "entropy" routine, and auto-plot frequency/log-size curves and individual particle-size-distribution (PSD) graphs.

Output graphs need adjustable scaling, clear group-bands, and publishable aesthetics.

### 2. Automatic Spatial Export

After processing, generate a KMZ file that ties each sample's modal group to its geographic coordinates so results open directly in Google Earth (no hand typing).

### 3. Mapping & Pathway Visualisation

UI should let the user pick several locations and display how modal grain size progresses along a hypothesised transport path on the seabed.

### 4. Modern, User-Friendly GUI

Single interface to: choose input CSV, set output file name, select composite vs. per-group outputs, watch progress, view graphs.

Goal: "nice GUI" that new users can operate without coding or Excel hacks.

### 5. Improved Output Management

Produce smaller, cleaner result files; avoid "too-big Excel" issues.

Export raw results plus enriched visuals (PNG/PDF) in one run.

### 6. Error-Free Automation

Eliminate manual steps that currently introduce copy-paste mistakes (e.g., matching sample names when mapping).

### 7. Extensibility & Publishability

Codebase should be clean enough to extend to other sediment-profile inputs, and polished enough to underpin a journal or conference publication.
