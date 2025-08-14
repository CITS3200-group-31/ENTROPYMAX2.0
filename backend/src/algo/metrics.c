#include "metrics.h"

// OWNER: Noah
// VB6 mapping: TOTALinequality → em_total_inequality
int em_total_inequality(const double *data, int32_t rows, int32_t cols,
                        double *out_Y, double *out_tineq){
  (void)data; (void)rows; (void)cols; (void)out_Y; (void)out_tineq;
  // TODO [Noah]: implement total inequality with base-2 logs (VB6 TOTALinequality)
  return -1; // placeholder
}

// OWNER: Noah
// VB6 mapping: CHTest → em_ch_stat (deterministic RNG for permutations)
int em_ch_stat(const double *class_table, int32_t samples, int32_t classes, int32_t k,
               int32_t perms_n, uint64_t seed,
               double *out_CH, double *out_sstt, double *out_sset,
               double *out_perm_mean, double *out_perm_p){
  (void)class_table; (void)samples; (void)classes; (void)k; (void)perms_n; (void)seed;
  (void)out_CH; (void)out_sstt; (void)out_sset; (void)out_perm_mean; (void)out_perm_p;
  // TODO [Noah]: implement CH pseudo-F and optional permutations (VB6 CHTest)
  return -1; // placeholder
}

// OWNER: Noah
// VB6 mapping: Z computation inside RITE → em_group_zstats
int em_group_zstats(const double *group_means, const int32_t *n_k, int32_t k, int32_t cols,
                    const double *TM, const double *SD, double *out_Z){
  (void)group_means; (void)n_k; (void)k; (void)cols; (void)TM; (void)SD; (void)out_Z;
  // TODO [Noah]: implement Z statistics (VB6 RITE: Z = (gmean - TM) / (SD/sqrt(n)))
  return -1; // placeholder
}

