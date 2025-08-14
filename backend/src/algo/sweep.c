#include "sweep.h"

// OWNER: Will
// VB6 mapping: LOOPgroupsize → em_sweep_k
int em_sweep_k(const double *data_in, int32_t rows, int32_t cols,
               int32_t k_min, int32_t k_max,
               int do_row_prop, int do_gdtl,
               int do_ch_perms, int32_t perms_n, uint64_t seed,
               int32_t *out_opt_k,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means){
  (void)data_in; (void)rows; (void)cols; (void)k_min; (void)k_max;
  (void)do_row_prop; (void)do_gdtl; (void)do_ch_perms; (void)perms_n; (void)seed;
  (void)out_opt_k; (void)out_metrics; (void)metrics_cap; (void)out_member1; (void)out_group_means;
  // TODO [Will]: implement k-range sweep, calling preprocessing flags as needed,
  //              compute tineq (Noah), optimise groups, compute Rs/CH per k,
  //              and select best k by max CH with tie-break to smallest k.
  return -1; // placeholder
}

