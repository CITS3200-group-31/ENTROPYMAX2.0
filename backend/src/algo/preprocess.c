#include "preprocess.h"

// OWNER: Noah line 787 in Form1
// VB6 mapping: Proportion → em_proportion
int em_proportion(double *data, int32_t rows, int32_t cols) {
    if (!data || rows <= 0 || cols <= 0) {
        return -1;
    }

    for (int i = 0; i < rows; ++i) {
        double row_sum = 0.0;

        // First pass: compute the sum of the row
        for (int j = 0; j < cols; ++j) {
            row_sum += data[i * cols + j];
        }

        if (row_sum == 0.0) {
            return -2;
        }

        // Second pass: divide each element in the row by the row sum
        for (int j = 0; j < cols; ++j) {
            data[i * cols + j] /= row_sum;
        }
    }

    return 0;
}

// OWNER: Noah line 463 in Form1
// VB6 mapping: GDTLproportion → em_gdtl_percent
int em_gdtl_percent(double *data, int32_t rows, int32_t cols){
    if (data == NULL || rows <= 0 || cols <= 0)
        return -1;

    double grand_total = 0.0;

    // calculate grand total (GDTL)
    for (int i = 0; i < rows * cols; ++i) {
        grand_total += data[i];
    }

    if (grand_total == 0.0)
        return -2; // divide zero check

    // convert to % 
    for (int i = 0; i < rows * cols; ++i) {
        data[i] = (data[i] / grand_total) * 100.0;
    }

    return 0; // Success
}

// OWNER: Noah Line 686 in Form1
// VB6 mapping: MeansSTdev → em_means_sd (with negative-variance guard)
int em_means_sd(const double *data, int32_t rows, int32_t cols, double *out_means, double *out_sd) {
    if (!data || !out_means || !out_sd || rows <= 0 || cols <= 0) {
        return -1;  // Invalid input
    }

    // Initialize means and SDs to zero
    for (int j = 0; j < cols; ++j) {
        out_means[j] = 0.0;
        out_sd[j] = 0.0;
    }

    // Accumulate sums and squared sums
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            double value = data[i * cols + j];
            out_means[j] += value;
            out_sd[j] += value * value;
        }
    }

    // Compute final mean and standard deviation for each column
    for (int j = 0; j < cols; ++j) {
        out_means[j] /= (double)rows;
        double mean_sq = out_means[j] * out_means[j];
        double avg_sq = out_sd[j] / (double)rows;
        double variance = avg_sq - mean_sq;

        // Handle negative variance
        if (variance < 0.0 && variance > -0.0001) {
            out_sd[j] = 0.0;
        } else if (variance >= 0.0) {
            out_sd[j] = sqrt(variance);
        } else {
            return -2;
        }
    }

    return 0;
}

