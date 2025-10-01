#pragma once
#include <stdint.h>
#include <math.h>
#include <stdlib.h>

/**
 * @brief Set groups based on member assignments.
 *
 * Organizes data into groups based on the provided membership array.
 *
 * @param data Pointer to the data array [rows * cols], row-major.
 * @param k Number of groups.
 * @param rows Number of rows in the data.
 * @param cols Number of columns in the data.
 * @param member1 Array indicating group membership for each row (0..k-1).
 * @param fGroupOut Output matrix buffer of shape [rows][cols+1] flattened row-major.
 *                  Caller allocates as a 2-D array of pointers or a single block; ownership remains with caller.
 *
 * @pre `data`, `member1`, and `fGroupOut` must not be NULL.
 * @pre `k`, `rows`, and `cols` must be greater than 0
 *
 * @return 0 on success, negative em_status_t on failure.
 */

int em_set_groups(const double *data, int32_t k, int32_t rows, int32_t cols,
                  const int32_t *member1, double **fGroupOut);

/**
 * @brief Initialize member1 array for a given number of rows and groups.
 *
 * Creates initial group assignments by distributing rows across k groups.
 * Typically assigns rows sequentially to groups.
 *
 * @param rows Number of rows in the data.
 * @param k Number of groups to create.
 * @param member1 Output array to store initial group assignments.
 *
 * @pre `member1` must not be NULL.
 * @pre `rows`, `k` must be greater than 0.
 *
 * @return 0 on success, -1 on failure.
 */

int em_initial_groups(int32_t rows, int32_t k, int32_t *member1);

/**
 * @brief Calculate between-group inequality statistic.
 *
 * Computes the inequality measure between different groups based on their
 * centroids and the overall data distribution. This is a key component
 * for calculating the RS statistic in clustering analysis.
 *
 * @param data Input data matrix (rows × cols).
 * @param rows Number of data points/samples.
 * @param cols Number of variables/features.
 * @param k Number of groups.
 * @param member1 Array of group assignments for each data point.
 * @param Y Array of variable totals/sums across all data.
 * @param out_bineq Output pointer for calculated between-group inequality.
 *
 * @pre All pointer parameters must not be NULL.
 * @pre `rows`, `cols`, `k` must be greater than 0.
 * @pre `member1[i]` values must be in range [0, k-1].
 *
 * @return 0 on success, negative value on error.
 */

int em_between_inequality(const double *data, int32_t rows, int32_t cols,
                          int32_t k, const int32_t *member1, const double *Y,
                          double *out_bineq);

/**
 * @brief Calculate RS (Relative Separation) statistic.
 *
 * Computes the RS statistic as a percentage: (between_inequality /
 * total_inequality) * 100. This measures how well the grouping separates the
 * data, with higher values indicating better separation between groups.
 *
 * @param tineq Total inequality across all data.
 * @param bineq Between-group inequality.
 * @param out_rs Output pointer for calculated RS statistic (percentage).
 * @param out_ixout Output flag: 0 if normal calculation, 1 if special case
 * handled.
 *
 * @pre `out_rs` and `out_ixout` must not be NULL.
 * @pre `tineq` and `bineq` should be non-negative.
 *
 * @return 0 on success, -1 on invalid input.
 *
 * @note Special cases: If tineq=0 and bineq=0, returns RS=100%. If tineq=0 but
 * bineq>0, returns RS=0%.
 */

int em_rs_stat(double tineq, double bineq, double *out_rs, int *out_ixout);

/**
 * @brief Optimize group assignment by accepting or rejecting a proposed change.
 *
 * Evaluates whether a proposed group assignment change improves the clustering
 * quality. If the new RS statistic is better, calculates new group centroids.
 * If worse, reverts to the previous assignment. This is a core component of
 * the iterative clustering optimization algorithm.
 *
 * @param data Input data matrix (rows × cols).
 * @param rows Number of data points/samples.
 * @param cols Number of variables/features.
 * @param k Number of groups.
 * @param rs_stat Current RS statistic for the proposed grouping.
 * @param best_stat Pointer to best RS statistic found so far (updated if
 * improvement).
 * @param member1 Array of group assignments (may be modified).
 * @param current_item Index of the item whose assignment was changed.
 * @param orig_group Original group assignment for current_item (for reversion).
 * @param iter_count Pointer to iteration counter (decremented if change
 * rejected).
 * @param min_groups Minimum number of groups constraint.
 * @param out_group_means Output array for group centroids (k × cols).
 *
 * @pre All pointer parameters must not be NULL.
 * @pre `rows`, `cols`, `k` must be greater than 0.
 * @pre `current_item` must be in range [0, rows-1].
 * @pre `orig_group` must be in range [0, k-1].
 *
 * @return 0 on success, negative value on error (-1: invalid input, -2: invalid
 * group assignment, -3: empty group).
 */

int em_optimise_groups(const double *data, int32_t rows, int32_t cols,
                       int32_t k, double rs_stat, double *best_stat,
                       int32_t *member1, int32_t current_item,
                       int32_t orig_group, int32_t *iter_count,
                       int32_t min_groups, double *out_group_means);

/**
 * @brief Perform iterative group switching optimization to find optimal
 * clustering.
 *
 * Implements the main clustering optimization algorithm by systematically
 * trying to move each data point to each possible group and keeping changes
 * that improve the RS statistic. Continues until no improvements are found for
 * 3 consecutive iterations, indicating convergence to a local optimum.
 *
 * @param data Input data matrix (rows × cols).
 * @param rows Number of data points/samples.
 * @param cols Number of variables/features.
 * @param k Number of groups.
 * @param tineq Total inequality across all data.
 * @param Y Array of variable totals/sums across all data.
 * @param min_groups Minimum number of groups constraint.
 * @param member1 Array of group assignments (modified in-place during
 * optimization).
 * @param out_bineq Output pointer for final between-group inequality.
 * @param out_rs_stat Output pointer for final RS statistic.
 * @param out_ixout Output flag from RS calculation.
 * @param out_group_means Output array for final group centroids (k × cols).
 *
 * @pre All pointer parameters must not be NULL.
 * @pre `rows`, `cols`, `k` must be greater than 0.
 * @pre `tineq` should be positive for meaningful results.
 * @pre `member1` should contain valid initial group assignments [0, k-1].
 *
 * @return 0 on success, -1 on invalid input.
 *
 * @note This function modifies `member1` in-place with the optimized group
 * assignments.
 * @note The algorithm explores rows × k different assignments per iteration.
 * @note Convergence is detected when no improvements are made for 3 consecutive
 * full iterations.
 */

int em_switch_groups(const double *data, int32_t rows, int32_t cols, int32_t k,
                     double tineq, const double *Y, int32_t min_groups,
                     int32_t *member1, double *out_bineq, double *out_rs_stat,
                     int32_t *out_ixout, double *out_group_means);
