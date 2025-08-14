#include "metrics.h"
#include <math.h>

static inline double log2_safe(double x){ return log(x)/log(2.0); }

int em_total_inequality(const double *data, int32_t rows, int32_t cols,
                        double *out_Y, double *out_tineq){
  for(int32_t j=0;j<cols;j++){ out_Y[j]=0.0; }
  for(int32_t j=0;j<cols;j++) for(int32_t i=0;i<rows;i++) out_Y[j]+=data[i*cols+j];
  double tineq=0.0;
  for(int32_t j=0;j<cols;j++){
    double Y = out_Y[j]; double X=0.0; if(Y<=0.0) continue;
    for(int32_t i=0;i<rows;i++){
      double v = data[i*cols+j]; if(v<=0.0) continue;
      X += (v/Y) * log2_safe(((double)rows * v)/Y);
    }
    tineq += Y * X;
  }
  *out_tineq = tineq;
  return 0;
}

int em_ch_stat(const double *class_table, int32_t samples, int32_t classes, int32_t k,
               int32_t perms_n, uint64_t seed,
               double *out_CH, double *out_sstt, double *out_sset,
               double *out_perm_mean, double *out_perm_p){
  (void)seed; // TODO deterministic RNG
  // Compute sstt and sset akin to VB6 CHTest (expects class_table shaped [samples x (classes+1)])
  // Placeholder: return not implemented
  (void)class_table; (void)samples; (void)classes; (void)k; (void)perms_n;
  (void)out_CH; (void)out_sstt; (void)out_sset; (void)out_perm_mean; (void)out_perm_p;
  return -1;
}

int em_group_zstats(const double *group_means, const int32_t *n_k, int32_t k, int32_t cols,
                    const double *TM, const double *SD, double *out_Z){
  for(int32_t gi=0; gi<k; ++gi){
    double div = (double)(n_k[gi]); if(div<=0.0) div = 1.0;
    for(int32_t j=0;j<cols;j++){
      double se = SD[j] / sqrt(div);
      double tt = group_means[gi*cols + j] - TM[j];
      out_Z[gi*cols + j] = (se==0.0)? 0.0 : (tt/se);
    }
  }
  return 0;
}

