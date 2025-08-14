#include "sweep.h"
#include "preprocess.h"
#include "metrics.h"
#include "grouping.h"
#include <stdlib.h>

int em_sweep_k(const double *data_in, int32_t rows, int32_t cols,
               int32_t k_min, int32_t k_max,
               int do_row_prop, int do_gdtl,
               int do_ch_perms, int32_t perms_n, uint64_t seed,
               int32_t *out_opt_k,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means){
  (void)do_ch_perms; (void)perms_n; (void)seed; // TODO perms
  if(k_min<2) k_min=2; if(k_max<k_min) k_max=k_min;
  // Make a working copy
  double *data = (double*)malloc(sizeof(double)*rows*cols); if(!data) return -1;
  for(int64_t i=0;i<(int64_t)rows*cols;i++) data[i]=data_in[i];
  if(do_row_prop) em_proportion(data, rows, cols);
  if(do_gdtl) em_gdtl_percent(data, rows, cols);

  double *Y = (double*)malloc(sizeof(double)*cols); if(!Y){ free(data); return -1; }
  double tineq=0.0; em_total_inequality(data, rows, cols, Y, &tineq);

  int32_t best_k=k_min; double best_ch=-1e300;
  int idx=0;
  for(int32_t k=k_min; k<=k_max && idx<metrics_cap; ++k){
    em_initial_groups(rows, k, out_member1);
    em_optimise_groups(data, rows, cols, k, tineq, out_member1, out_group_means);
    // Placeholder: compute CH via metrics API later; set rs placeholder 0
    double bineq=0.0; em_between_inequality(data, rows, cols, k, out_member1, Y, &bineq);
    double rs=0.0; int ix=0; em_rs_stat(tineq, bineq, &rs, &ix);
    double ch=rs; // temporary stand-in until CH implemented
    out_metrics[idx].k = k; out_metrics[idx].ch_value = ch; out_metrics[idx].rs_percent = rs; idx++;
    if(ch>best_ch){ best_ch=ch; best_k=k; }
  }
  *out_opt_k = best_k; free(Y); free(data); return 0;
}

