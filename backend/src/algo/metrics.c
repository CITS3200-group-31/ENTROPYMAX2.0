#include "metrics.h"

// OWNER: Noah line 1106 in Form1
// VB6 mapping: TOTALinequality → em_total_inequality
int em_total_inequality(const double *data, int32_t rows, int32_t cols,
                        double *out_Y, double *out_tineq) {
    if (!data || !out_Y || !out_tineq) {
        return -1; 
    }

    for (int j = 0; j < cols; j++) {
        out_Y[j] = 0.0;
    }
    *out_tineq = 0.0;

    for (int j = 0; j < cols; j++) {
        for (int i = 0; i < rows; i++) {
            out_Y[j] += data[i * cols + j];
        }
    }

    for (int j = 0; j < cols; j++) {
        double Yj = out_Y[j];
        if (Yj == 0.0) {
            continue;
        }

        double X = 0.0;
        for (int i = 0; i < rows; i++) {
            double val = data[i * cols + j];
            if (val > 0.0) {
                double ratio = val / Yj;
                double argument = (rows * val) / Yj;
                X += ratio * log2(argument);
            }
        }
        *out_tineq += Yj * X;
    }
    return 0;

// OWNER: Noah line 1140 in Form1
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

// OWNER: Noah line 810 in Form1
// VB6 mapping: Z computation inside RITE → em_group_zstats
int em_group_zstats(const double *group_means, const int32_t *n_k, int32_t k,                 
                    int32_t cols, const double *TM, const double *SD, double *out_Z) {             
    if (!group_means || !n_k || !TM || !SD || !out_Z) {
        return -1;
    }

    for (int group = 0; group < k; group++) {
        int n = n_k[group];
        if (n <= 0) {
            for (int col = 0; col < cols; col++) {
                out_Z[group * cols + col] = 0.0; 
            }
            continue;
        }

        double sqrt_n = sqrt((double)n);

        for (int col = 0; col < cols; col++) {
            double se = SD[col] / sqrt_n;
            if (se == 0.0) {
                out_Z[group * cols + col] = 0.0;
            } else {
                double diff = group_means[group * cols + col] - TM[col];
                out_Z[group * cols + col] = diff / se;
            }
        }
    }

    return 0;
}

