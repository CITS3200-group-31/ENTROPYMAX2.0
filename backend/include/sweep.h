#pragma once
#include <stdint.h>

typedef struct {
  int32_t k;
  double ch_value;
  double rs_percent;
} em_k_metric_t;

// Run sweep over k in [k_min, k_max] and select best k by max CH (tie-break to smallest k)
int em_sweep_k(const double *data, int32_t rows, int32_t cols,
               int32_t k_min, int32_t k_max,
               int do_row_prop, int do_gdtl,
               int do_ch_perms, int32_t perms_n, uint64_t seed,
               int32_t *out_opt_k,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means);

