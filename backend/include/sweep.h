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

/**
 * @brief Sweep through group sizes to find optimal k.
 *
 * This function evaluates clustering solutions for group sizes ranging from
 * `k_min` to `k_max`, calculating various metrics for each k. It identifies
 * the optimal number of groups based on the highest Calinski-Harabasz
 * statistic.
 *
 * @param data_in Input data matrix (rows x cols).
 * @param rows Number of data points (rows).
 * @param cols Number of variables (columns).
 * @param Y Array of variable totals/sums across all data.
 * @param tineq Total inequality across all data.
 * @param k_min Minimum number of groups to consider.
 * @param k_max Maximum number of groups to consider.
 * @param out_opt_k Pointer to store the optimal number of groups.
 * @param perms_n Number of permutations to perform.
 * @param seed Seed for random number generator.
 * @param out_metrics Array to store metrics for each k.
 * @param metrics_cap Maximum number of metrics to store.
 * @param out_member1 Array to store group assignments for the optimal k.
 * @param out_group_means Array to store group centroids for the optimal k.
 *
 * @pre All pointer parameters must not be NULL.
 * @pre `rows`, `cols`, `k_min`, `k_max`, and `metrics_cap` must be greater than
 * 0.
 * @pre `k_max` must be greater than or equal to `k_min`.
 *
 * @return 0 on success, -1 on failure.
 */

// OWNER: Will
// VB6 mapping: LOOPgroupsize → em_sweep_k
int em_sweep_k(const double *data_in, int32_t rows, int32_t cols,
               const double *Y, double tineq, int32_t k_min, int32_t k_max,
               int32_t *out_opt_k, int32_t perms_n, uint64_t seed,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means);
