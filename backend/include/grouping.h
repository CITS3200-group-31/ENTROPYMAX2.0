#pragma once
#include <stdint.h>

/**
 * @brief Set groups based on member assignments.
 *
 * This function organizes data into groups based on the provided membership array.
 *
 * @param data Pointer to the data array.
 * @param ng Number of groups.
 * @param rows Number of rows in the data.
 * @param cols Number of columns in the data.
 * @param member1 Array indicating group membership for each row.
 * @param fGroupOut Output array to store group data.
 *
 * @pre `data`, `member1`, and `fGroupOut` must not be NULL.
 * @pre `ng`, `rows`, and `cols` must be greater than 0
 *
 * @return 0 on success, -1 on failure.
 */

int em_set_groups(const double *data, int32_t ng, int32_t rows, int32_t cols,
                  const int32_t *member1, double **fGroupOut);

/**
 * @brief
 *
 *
 *
 *
 *
 *
 */

int em_initial_groups(int32_t rows, int32_t k, int32_t *member1);

/**
 * @brief
 *
 *
 *
 *
 *
 *
 */

int em_between_inequality(const double *data, int32_t rows, int32_t cols,
                          int32_t k, const int32_t *member1,
                          const double *Y, double *out_bineq);

/**
 * @brief
 *
 *
 *
 *
 *
 *
 */

int em_rs_stat(double tineq, double bineq, double *out_rs, int *out_ixout);

/**
 * @brief
 *
 *
 *
 *
 *
 *
 */

int em_optimise_groups(const double *data, int32_t rows, int32_t cols,
                       int32_t k, double tineq,
                       int32_t *member1, double *out_group_means);
