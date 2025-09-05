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
}
// OWNER: Noah line 1140 in Form1
// VB6 mapping: CHTest → em_ch_stat (deterministic RNG for permutations)
int em_ch_stat(const double *class_table, int32_t samples, int32_t classes, int32_t k,
               int32_t perms_n, uint64_t seed,
               double *out_CH, double *out_sstt, double *out_sset,
               double *out_perm_mean, double *out_perm_p)
{
    if (!class_table || samples <= 0 || classes <= 0 || k <= 1) return -1;

    int i, j;
    double *totsum = calloc((size_t)classes, sizeof(double));
    double *totav  = calloc((size_t)classes, sizeof(double));
    double *sst    = calloc((size_t)classes, sizeof(double));
    double **clsum = calloc((size_t)k, sizeof(double*));
    double *clsam  = calloc((size_t)k, sizeof(double));
    double **clav  = calloc((size_t)k, sizeof(double*));
    double **sse   = calloc((size_t)k, sizeof(double*));

    if (!totsum || !totav || !sst || !clsum || !clsam || !clav || !sse) return -1;

    for (i = 0; i < k; i++) {
        clsum[i] = calloc((size_t)classes, sizeof(double));
        clav[i] = calloc((size_t)classes, sizeof(double));
        sse[i] = calloc((size_t)classes, sizeof(double));
        if (!clsum[i] || !clav[i] || !sse[i]) return -1;
    }

    double sstt = 0.0, sset = 0.0;
    double r = 0.0;

    
    for (j = 0; j < classes; j++) {
        for (i = 0; i < samples; i++) {
            int cluster = (int)class_table[i * (classes + 1)];
            double value = class_table[i * (classes + 1) + j + 1];
            totsum[j] += value;
            clsum[cluster][j] += value;
            clsam[cluster] += 1.0;
        }
    }

    for (j = 0; j < classes; j++) {
        totav[j] = totsum[j] / samples; // Samples, averages for total centroid
    }

    
    for (i = 0; i < k; i++) { // Averages within group and classes 
        if (clsam[i] == 0) {
            *out_CH = 0.1;
            goto cleanup;
        }
        for (j = 0; j < classes; j++) {
            clav[i][j] = clsum[i][j] / clsam[i];
        }
    }

    for (j = 0; j < classes; j++) { // Calculate total sum of squares
        for (i = 0; i < samples; i++) {
            int cluster = (int)class_table[i * (classes + 1)];
            double value = class_table[i * (classes + 1) + j + 1];
            sst[j] += pow(value - totav[j], 2);
            sse[cluster][j] += pow(value - clav[cluster][j], 2);
        }
        sstt += sst[j];
    }

    for (i = 0; i < k; i++) { // calculate total within group sum of squares
        for (j = 0; j < classes; j++) {
            sset += sse[i][j];
        }
    }

    *out_sstt = sstt;
    *out_sset = sset;

    r = (sstt - sset) / sstt;
    if (r == 1.0) {
        *out_CH = INFINITY;
        goto cleanup;
    }

    *out_CH = (r / (k - 1)) / ((1 - r) / (samples - k));

    // for if permutations are requested
    if (perms_n > 0) {
        double perm_sum = 0.0;
        int perm_better = 0;
        double *perm_data = malloc((size_t)samples * (size_t)(classes + 1) * sizeof(double));
        if (!perm_data) goto cleanup;

        memcpy(perm_data, class_table, (size_t)samples * (size_t)(classes + 1) * sizeof(double));
        srand((unsigned int)seed);

        for (int p = 0; p < perms_n; p++) {
            for (j = 0; j < classes; j++) {
                for (i = 0; i < samples; i++) {
                    int idx1 = i;
                    int idx2 = rand() % samples;
                    double tmp = perm_data[idx1 * (classes + 1) + j + 1];
                    perm_data[idx1 * (classes + 1) + j + 1] = perm_data[idx2 * (classes + 1) + j + 1];
                    perm_data[idx2 * (classes + 1) + j + 1] = tmp;
                }
            }

            double ch_tmp, sst_tmp, sse_tmp;
            double dummy;
            em_ch_stat(perm_data, samples, classes, k, 0, 0, &ch_tmp, &sst_tmp, &sse_tmp, &dummy, &dummy);

            perm_sum += ch_tmp;
            if (ch_tmp > *out_CH) perm_better++;
        }

        *out_perm_mean = perm_sum / perms_n;
        *out_perm_p = (double)perm_better / perms_n;

        free(perm_data);
    } else {
        *out_perm_mean = 0;
        *out_perm_p = 0;
    }

cleanup:
    free(totsum); free(totav); free(sst); free(clsam);
    for (i = 0; i < k; i++) {
        free(clsum[i]); free(clav[i]); free(sse[i]);
    }
    free(clsum); free(clav); free(sse);
    return 0;
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

