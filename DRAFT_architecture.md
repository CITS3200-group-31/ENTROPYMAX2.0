# EntropyMax 2.0 – Architecture

## Overview
EntropyMax 2.0 separates heavy numerical work from user‑facing code:

```
CSV ─▶ libentropymax (C 11) ─▶ NumPy array ─▶ PyQt 6 GUI ─▶ plots / exports
```

* **C 11 core (`libentropymax`)**   Fast, portable port of the legacy VBA algorithms.  
* **Python binding (`entropymax` pkg)**   Cython/cffi wrapper → NumPy, pandas.  
* **PyQt 6 front‑end**   Import wizard, live plotting/mapping, one‑click exports.  
* **R / notebooks**   `reticulate` or direct C ABI for advanced analytics.

## Text diagram
```
                               PyQt 6 GUI
                               (Plotly / Matplotlib)
                                       ▲ NumPy / pandas
CLI / notebooks ─ entropymax pkg ──────┘
        ▲  Cython / cffi
        │  stable C ABI
        ▼
      libentropymax (C 11)
      CSV in  ─▶  algorithms  ─▶  CSV / arrays out
```

## Components
| Component | Main responsibilities |
|-----------|-----------------------|
| **libentropymax** | Parse CSV, run grain‑size grouping, return arrays / CSV. |
| **entropymax.core** | Thin wrapper around C ABI (`em_init`, `em_run`). |
| **entropymax.io** | Convenience helpers (CSV ⇆ pandas). |
| **entropymax.vis** | Shared Plotly / Matplotlib utilities. |
| **entropymax.cli** | Headless batch runner (`python -m entropymax`). |
| **PyQt GUI** | Wizards, plots, map view, export panel. |

## Roles & effort (indicative)
```
[C team]      35 % – port & unit‑test algorithms
[Bindings]    15 % – Cython/cffi, wheel packaging
[GUI devs]    35 % – PyQt widgets, plotting, mapping
[Data/R]      10 % – sample datasets, R notebook demos
[DevOps]       5 % – CI, cross‑compile, installers
```

## Key advantages
* **Speed + stability** – C core is lightning‑fast and ABI‑stable.  
* **Developer velocity** – most day‑to‑day work happens in Python.  
* **Flexible UI future** – any front‑end can talk to Python or C directly.  

## Immediate next steps
1. Spike‑port one VBA routine to C; wrap with cffi; plot in PyQt.  
2. Finalise C header & semantic versioning rules.  
3. Stand up GitHub Actions matrix (Win/macOS/Linux) for cross‑build.  
4. Lock PyQt window structure & styling guide.
