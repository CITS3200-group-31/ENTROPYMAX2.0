#pragma once
#include <stdint.h>

// Row-wise proportion normalisation
int em_proportion(double *data, int32_t rows, int32_t cols);

// Grand-total normalisation to percentages
int em_gdtl_percent(double *data, int32_t rows, int32_t cols);

// Means and standard deviations with negative-variance guard
int em_means_sd(const double *data, int32_t rows, int32_t cols,
                double *out_means, double *out_sd);

