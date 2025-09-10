# Porting Guide: VB6 → C backend

This guide maps each legacy VB6 routine to its C counterpart, shows ownership, and points to the correct file to implement. The intended pipeline is:

CSV(gps) + CSV(raw) → merged raw Parquet → C backend → processed Parquet.

## Owners
- Ben: I/O (CSV load, future Parquet/CSV write)
- Noah: Preprocess + Metrics (row/grand‑total normalisation, means/SD, total inequality, CH, Z)
- Will: Grouping + Sweep (initial groups, between‑inequality, Rs, greedy optimiser, loop over k)
- Steve: Final data write/packaging

## Function mapping

- FileK3 → csv_read_table (Ben)
  - File: `backend/src/io/csv_reader.c`
  - Header: `backend/include/csv.h`

- SetGroups → em_set_groups (Will)
  - File: `backend/src/algo/grouping.c`
  - Header: `backend/include/grouping.h`

- INITIALgroup → em_initial_groups (Will)
  - File: `backend/src/algo/grouping.c`

- SWITCHgroup/OPTIMALgroup → em_optimise_groups (Will)
  - File: `backend/src/algo/grouping.c`

- LOOPgroupsize → em_sweep_k (Will)
  - File: `backend/src/algo/sweep.c`

- MeansSTdev → em_means_sd (Noah)
  - File: `backend/src/algo/preprocess.c`

- TOTALinequality → em_total_inequality (Noah)
  - File: `backend/src/algo/metrics.c`

- BETWEENinquality → em_between_inequality (Will)
  - File: `backend/src/algo/grouping.c`

- RSstatistic → em_rs_stat (Will)
  - File: `backend/src/algo/grouping.c`

- CHTest → em_ch_stat (Noah)
  - File: `backend/src/algo/metrics.c`

- Proportion → em_proportion (Noah)
  - File: `backend/src/algo/preprocess.c`

- GDTLproportion → em_gdtl_percent (Noah)
  - File: `backend/src/algo/preprocess.c`

- BESTgroup → covered by final outputs; Z by em_group_zstats (Noah)
  - File: `backend/src/algo/metrics.c`

- RITE (Z stats) → em_group_zstats (Noah)
  - File: `backend/src/algo/metrics.c`

- SAVEdata → parquet_write_table (Steve) (interim CSV writer optional)
  - File: `backend/src/io/parquet_writer.c`

## Entry point

- `em_run_algo` (glue/orchestration)
  - File: `backend/src/algo/backend_algo.c`
  - Flow: read raw Parquet (via loader) → preprocess → sweep k → write processed Parquet

## Numerical rules to preserve
- Base‑2 logarithms throughout
- Zero checks to avoid log(0)
- Negative‑variance guard in SD
- Initial groups: equal blocks; remainder to last group
- Rs special case: if tineq=0 and bineq=0 → Rs=100 and ixout=1

## Determinism
- CH permutations must use a deterministic RNG with a configurable seed
