#pragma once
#include <stdint.h>

// Initialise equal-sized groups; member1[rows] gets values 1..k
int em_initial_groups(int32_t rows, int32_t k, int32_t *member1);

// Between-group inequality given assignments and per-variable totals Y[cols]
int em_between_inequality(const double *data, int32_t rows, int32_t cols,
                          int32_t k, const int32_t *member1,
                          const double *Y, double *out_bineq);

// Rs statistic helper (edge cases handled as in legacy)
int em_rs_stat(double tineq, double bineq, double *out_rs, int *out_ixout);

// Greedy optimise assignments for fixed k. Updates member1 and group means.
int em_optimise_groups(const double *data, int32_t rows, int32_t cols,
                       int32_t k, double tineq,
                       int32_t *member1, double *out_group_means);

