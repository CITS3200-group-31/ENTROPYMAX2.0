# Legacy code analysis – Form1.frm and Module1.bas (Archived)

This explains what the legacy VB6 code does, focusing on the computational routines to port to C and separating Windows/UI details. For the active plan and implementation, see `docs/ARCHITECTURE.md`, `docs/PORTING_GUIDE.md`, and `docs/BACKEND.md`.

## High‑level pipeline (triggered by Proceed)
- Read CSV into arrays (samples × variables)
- Optional per‑row normalisation to proportions
- Grand‑total normalisation to percentages
- Compute per‑variable means (TM) and standard deviations (SD)
- Compute total inequality (tineq)
- For k in 2..20 (or user range): initialise groups, greedily reassign to improve Rs (explained %), record CH and Rs
- Choose optimal k (max CH), compute group Z statistics

## Key arrays and terms
- jobs: number of samples; nvar: number of variables
- CLtitle(nvar+1): column headers; first is row‑title header
- RWTitle(jobs): row/sample identifiers
- result(jobs,nvar): transformed data matrix; sData(jobs,nvar): original copy
- TM(nvar), SD(nvar): per‑variable mean and standard deviation
- Y(nvar): per‑variable totals
- member1(jobs): current group assignment 1..k
- sumx(k,nvar), gmean(k,nvar): per‑group means (working/output)
- RsGraph: per‑k [k, CH, Rs]; CHsstsse: SST/SSE/perm stats

## Functions to port to C (as‑is semantics)
- Proportion: per‑row normalisation (if enabled)
- GDTLproportion: grand‑total normalisation to percentages
- MeansSTdev: means and SDs (guard small negative variance)
- TOTALinequality: base‑2 log formula over variables
- BETWEENinquality: between‑group inequality for assignments
- RSstatistic: Rs = 100 * between / total (edge‑case handling)
- INITIALgroup: equal‑sized initial grouping
- SWITCHgroup: greedy reassignment loop + metrics
- OPTIMALgroup: accept if Rs improves; recompute per‑group means
- LOOPgroupsize: sweep k, run optimisation, collect metrics
- CHTest: Calinski–Harabasz pseudo‑F; optional permutations
- RITE: per‑group Z statistics from group vs overall mean/SD

## Functions to drop/relocate (UI/logging)
- GetSaveFile (Windows file dialogs)
- MSChart configuration, clipboard copy, HtmlHelp calls
- Temp file `c:\column` and CSV/log file writes in SAVEdata/RITE

## Numerical details to preserve
- Base‑2 logarithms; skip zero terms
- Negative variance guard: if (E[x^2] − mean^2) ∈ (−1e−4, 0) → 0
- Remainder samples assigned to last group in initialisation
- Rs special case: if tineq=0 and bineq=0 → Rs=100 and ixout=1

## CSV dialect in FileK3
- First row: nvar+1 fields (row‑title header + variable names)
- Subsequent rows: sample ID then nvar numeric fields
- Modern port: single‑pass parse, in‑memory only

## CH statistic and permutations
- CH = (r/(k−1)) / ((1−r)/(Samples−k)) with r = (sstt−sset)/sstt
- Optional permutations (100 in VB) randomise columns per row; adopt deterministic seed in C

This document pairs with extensive comments embedded directly in `legacy/Form1.frm` and `legacy/Module1.bas` for line‑by‑line guidance.
