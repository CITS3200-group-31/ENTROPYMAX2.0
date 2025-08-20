# Legacy VB6 Code - EntropyMax Algorithm

This directory contains the original VB6 implementation of the EntropyMax algorithm, which is being ported to C for ENTROPYMAX 2.0. The code implements entropy-based classification using information statistics as described in Johnson & Semple (1983).

## Current Files

- **`Form1.frm`** - Main form containing the core algorithm implementation
- **`Module1.bas`** - Global types and Windows API declarations
- **`EntropyMax.vbp`** - VB6 project file (metadata only)
- **`legacy_documentation.chm`** - Original help documentation
- **`code_analysis.md`** - Detailed code analysis (superseded by this readme)
- **`legacy_readme.md`** - Previous audit (superseded by this readme)

## Algorithm Overview

The algorithm performs entropy-based classification with the following pipeline:

1. **Data Loading** - Read CSV into arrays (samples × variables)
2. **Preprocessing** - Optional row proportions; grand-total normalization to percentages
3. **Statistics** - Compute means, standard deviations, and total inequality
4. **Grouping Search** - Sweep k=2..20, optimize assignments using greedy reassignment
5. **Evaluation** - Compute Calinski-Harabasz (CH) pseudo-F and Rs (explained %) statistics
6. **Output** - Select optimal k, compute group Z-statistics

## Core Functions to Port

### Data Processing (Noah)
- `Proportion()` - Per-row normalization to proportions
- `GDTLproportion()` - Grand-total normalization to percentages
- `MeansSTdev()` - Column means and standard deviations
- `TOTALinequality()` - Total inequality using base-2 logs
- `CHTest()` - Calinski-Harabasz pseudo-F with optional permutations
- `RITE()` - Per-group Z-statistics

### Grouping Engine (Will)
- `INITIALgroup()` - Equal-sized initial grouping
- `SWITCHgroup()` - Greedy reassignment loop
- `OPTIMALgroup()` - Accept/reject reassignments
- `BETWEENinquality()` - Between-group inequality
- `RSstatistic()` - Percentage explained (Rs)
- `LOOPgroupsize()` - Sweep group counts and select optimum

### I/O (Ben)
- `FileK3()` - CSV reading (replace with modern parser)
- `SAVEdata()` - Output writing (replace with Parquet)

## Key Data Structures

- `result(jobs,nvar)` - Transformed data matrix
- `sData(jobs,nvar)` - Original data copy
- `member1(jobs)` - Current group assignments (1..k)
- `TM(nvar)`, `SD(nvar)` - Per-variable means and standard deviations
- `Y(nvar)` - Per-variable totals
- `sumx(k,nvar)`, `gmean(k,nvar)` - Per-group means

## Numerical Rules to Preserve

- **Logarithms**: Base-2 throughout; skip zero terms
- **Variance Guard**: If `(E[x²] - mean²) ∈ (-1e-4, 0)` → set SD to 0
- **Rs Edge Case**: If `tineq=0` and `bineq=0` → `Rs=100`
- **Group Initialization**: Remainder samples assigned to last group
- **Tie-breaking**: Highest CH; if tie, choose smallest k
- **Precision**: Use `double` in C port

## CSV Format

- First row: `nvar+1` fields (row-title header + variable names)
- Subsequent rows: Sample ID + `nvar` numeric fields
- Comma-separated, no temp files in modern port

## CH Statistic Details

- Formula: `CH = (r/(k-1)) / ((1-r)/(Samples-k))` where `r = (SST-SSE)/SST`
- Permutations: Default 100, use deterministic RNG with configurable seed
- SST = total sum of squares, SSE = within-group sum of squares

## Functions to Drop (UI/Windows)

- `GetSaveFile()` - Windows common dialogs
- Chart configuration and clipboard operations
- File dialogs and temp file handling
- All `Print #` statements and log file writes
- Windows API calls (`SetCursorPos`, `HtmlHelp`)

## Porting Status

The VB6 code has been fully audited and commented. The C backend structure is established with:

- **`backend/src/algo/preprocess.c`** - Noah's preprocessing tasks
- **`backend/src/algo/metrics.c`** - Noah's statistics tasks
- **`backend/src/algo/grouping.c`** - Will's grouping engine
- **`backend/src/algo/sweep.c`** - Will's k-sweep orchestration
- **`backend/src/io/csv_reader.c`** - Ben's CSV parser
- **`backend/src/io/parquet_writer.c`** - Ben's output writer

Each function is scaffolded with placeholders and clear VB6→C mappings. See `../backend_readme.md` for detailed allocation and workflow.

## References

- Johnson, R.J. & Semple, R.K. (1983). *Classification Using Information Statistics*. Geobooks, Norwich.
- Original QBasic code by Katsu Michibayashi
- Modifications by James Lally (James Cook University)
- VB6 conversion by L.K. Stewart (CSIRO Land and Water, 2005)
