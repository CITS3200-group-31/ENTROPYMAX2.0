#pragma once
#include <stdint.h>
#include <math.h>


/**
 * @brief computes total inequality metric for a dataset
 * Initialise sums to zero, then sum the data for each column.
 * Computes the total inequality metric based on the data provided. 
 * 
 * @param data pointer to the array
 * @param rows number of rows in the array
 * @param cols number of columns in the array
 * @param out_Y pointer to an array to store the sums for each column
 * @param out_tineq pointer to store the total inequality metric
 *
 * @return 0 on success, -1 on invalid input
 */

 int em_total_inequality(const double *data, int32_t rows, int32_t cols,
                        double *out_Y, double *out_tineq);


/**
 * @brief
 *
 *
 *
 *
 *
 *
 */
 
int em_ch_stat(const double *class_table, int32_t samples, int32_t classes, int32_t k,
               int32_t perms_n, uint64_t seed,
               double *out_CH, double *out_sstt, double *out_sset,
               double *out_perm_mean, double *out_perm_p);


/**
 * @brief computes Z statistics for group means (distance from global mean)
 * 
 * @param group_means Array of group means
 * @param n_k Array of sample sizes for each group
 * @param k Number of groups
 * @param cols Number of columns (variables)
 * @param TM Global mean vector
 * @param SD Standard deviation vector
 * @param out_Z Output array for Z statistics
 *
 * @return 0 on success, -1 on error
 */
 
int em_group_zstats(const double *group_means, const int32_t *n_k, int32_t k, int32_t cols,
                    const double *TM, const double *SD, double *out_Z);

