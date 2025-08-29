#pragma once
#include <stdint.h>

typedef struct {
  int32_t nGrpDum;
  double fCHDum;         // Calinski-Harabasz value
  double fRs;            // R-squared statistic
  double fSST;           // Total sum of squares (original)
  double fSSE;           // Error sum of squares (original)
  double fCHF;           // Total sum of squares (permuted)
  double fCHP;           // C-H value from permutation
  double nCounterIndex;  // C-H probability
} em_k_metric_t;

// Run sweep over k in [k_min, k_max] and select best k by max CH (tie-break to
// smallest k)
int em_sweep_k(const double *data_in, int32_t rows, int32_t cols,
               const double *Y, double tineq, int32_t k_min, int32_t k_max,
               int32_t *out_opt_k, int32_t perms_n, uint64_t seed,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means);
