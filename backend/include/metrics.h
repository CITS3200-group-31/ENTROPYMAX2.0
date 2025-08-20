#pragma once
#include <stdint.h>
#include <math.h>


/**
 * @brief
 *
 *
 *
 *
 *
 *
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
 * @brief
 *
 *
 *
 *
 *
 *
 */
 
int em_group_zstats(const double *group_means, const int32_t *n_k, int32_t k, int32_t cols,
                    const double *TM, const double *SD, double *out_Z);

