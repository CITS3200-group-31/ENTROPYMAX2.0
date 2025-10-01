#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Public entrypoint for the C backend
#include "algo.h"

// Module APIs (split by responsibility)
#include "preprocess.h"   // row/grand-total normalisation; means/SD
#include "metrics.h"      // total inequality; CH; Z statistics
#include "grouping.h"     // initial groups; between-inequality; optimiser
#include "sweep.h"        // k-sweep orchestration and metrics
#include "parquet.h"      // output writer (stubbed for now)

// A thin orchestration that wires the backend modules together.
// Inputs:
//  - data:      row-major [rows * cols] numeric matrix
//  - colnames:  optional column names (size cols)
//  - rownames:  optional row names (size rows)
//  - parquet_out_path: output path; if NULL, skip writing
// Behaviour:
//  - Applies default preprocessing (row proportions + grand-total %)
//  - Sweeps k=2..20, selects best k by CH (tie-break to smallest k)
//  - Writes final table to Parquet (placeholder writer)
int em_run_algo(const double *data,
                int32_t rows,
                int32_t cols,
                const char *const *colnames,
                const char *const *rownames,
                const char *parquet_out_path){
  if(rows<=0 || cols<=0 || data==NULL){
    return -1; // invalid input
  }

  // Make a working copy so we can apply preprocessing without mutating caller memory.
  double *work = (double*)malloc((size_t)rows * (size_t)cols * sizeof(double));
  if(!work) return -2;
  memcpy(work, data, (size_t)rows * (size_t)cols * sizeof(double));

  // Default preprocessing mirroring typical VB6 runs: row proportions + grand-total %
  // (These can be made configurable later via em_config_t.)
  (void)em_proportion(work, rows, cols);
  (void)em_gdtl_percent(work, rows, cols);

  // Allocate outputs for sweep. We reuse these buffers across k.
  int32_t *member1 = (int32_t*)malloc((size_t)rows * sizeof(int32_t));
  double  *group_means = (double*)malloc((size_t)20 * (size_t)cols * sizeof(double)); // max k=20
  em_k_metric_t metrics[32]; // capacity for k=2..20
  if(!member1 || !group_means){ free(work); free(member1); free(group_means); return -3; }

  // Prepare and sweep across k=2..20 with deterministic defaults (no permutations yet).
  double tineq = 0.0;
  int rc = em_prepare_and_sweep(/*data_proc*/ work, rows, cols,
                                /*k_min*/ 2, /*k_max*/ 20,
                                /*perms_n*/ 0, /*seed*/ 42u,
                                metrics, (int32_t)(sizeof(metrics)/sizeof(metrics[0])),
                                member1, group_means, NULL,
                                &tineq);
  if(rc!=0){ free(work); free(member1); free(group_means); return rc; }

  // Optional: write final data to Parquet (placeholder implementation returns -1 currently).
  int wrc = 0;
  if(parquet_out_path){
    wrc = parquet_write_table(parquet_out_path, work, rows, cols, colnames, rownames);
    // Ignore write failure for now, but surface non-zero code.
  }

  free(work);
  free(member1);
  free(group_means);
  return wrc; // 0 if write succeeded or was skipped; non-zero if writer failed
}

