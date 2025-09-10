#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "sweep.h"

// gcc -Ibackend/include -o test_sweep     backend/src/algo/test_sweep.c     backend/src/algo/sweep.c     backend/src/algo/grouping.c     backend/src/algo/metrics.c     -lm

int main() {
    // Example data: 20 rows, 4 columns
    int32_t rows = 20, cols = 4;
    double data_in[20 * 4] = {
        1, 2, 3, 4,
        2, 4, 6, 8,
        5, 5, 5, 5,
        1, 3, 5, 7,
        2, 1, 2, 1,
        3, 6, 9, 12,
        4, 8, 12, 16,
        5, 10, 15, 20,
        6, 12, 18, 24,
        7, 14, 21, 28,
        8, 16, 24, 32,
        9, 18, 27, 36,
        10, 20, 30, 40,
        11, 22, 33, 44,
        12, 24, 36, 48,
        13, 26, 39, 52,
        14, 28, 42, 56,
        15, 30, 45, 60,
        16, 32, 48, 64,
        17, 34, 51, 68
    };

    // Dummy Y and tineq (normally from em_total_inequality)
    double Y[4] = {0.1, 0.2, 0.3, 0.4};
    double tineq = 1.23;

    // Sweep k from 2 to 20
    int32_t k_min = 2, k_max = 20;
    int32_t perms_n = 10;
    uint64_t seed = 42;

    int metrics_cap = k_max - k_min + 1;
    em_k_metric_t metrics[metrics_cap];
    int32_t out_opt_k = 0;
    int32_t out_member1[rows];
    double out_group_means[k_max * cols];

    int result = em_sweep_k(
        data_in, rows, cols,
        Y, tineq, k_min, k_max,
        &out_opt_k, perms_n, seed,
        metrics, metrics_cap,
        out_member1, out_group_means
    );

    printf("em_sweep_k result: %d\n", result);
    printf("Optimal k: %d\n", out_opt_k);

    for (int i = 0; i < result; ++i) {
        printf("k=%d: CH=%.4f Rs=%.4f SST=%.4f SSE=%.4f CHF=%.4f CHP=%.4f PermMean=%.4f\n",
            metrics[i].nGrpDum,
            metrics[i].fCHDum,
            metrics[i].fRs,
            metrics[i].fSST,
            metrics[i].fSSE,
            metrics[i].fCHF,
            metrics[i].fCHP,
            metrics[i].nCounterIndex
        );
    }

    printf("Best group assignments:\n");
    for (int i = 0; i < rows; ++i) {
        printf("Row %d: Group %d\n", i, out_member1[i]);
    }

    printf("Best group means:\n");
    int best_k = out_opt_k;
    for (int g = 0; g < best_k; ++g) {
        printf("Group %d: ", g);
        for (int j = 0; j < cols; ++j) {
            printf("%.4f ", out_group_means[g * cols + j]);
        }
        printf("\n");
    }

    return 0;
}