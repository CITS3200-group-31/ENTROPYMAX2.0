#pragma once
#include <stdint.h>
#include <math.h>


/**
 * @brief creates a row-wise proportion of each element in an array
 * 
 * for each row in the array, we compute the sum of that row
 * 
 * then divide each element in that row by the sum
 * @param data pointer to the array
 * @param rows number of rows in the array
 * @param cols number of columns in the array
 *
 * @return 0 on success, -1 on invalid input, -2 on divide-by
 */

int em_proportion(double *data, int32_t rows, int32_t cols);


/**
 * @brief Calculates a percentage of the grand total of all elements in an array
 *
 * @param data pointer to the array
 * @param rows number of rows in the array
 * @param cols number of columns in the array
 *
 * @return 0 on success, -1 on invalid input, -2 on divide-by-zero
 */

int em_gdtl_percent(double *data, int32_t rows, int32_t cols);


/**
 * @brief calculates the mean and standard deviation for each column in an array
 *
 * @param data pointer to the array
 * @param rows number of rows in the array
 * @param cols number of columns in the array
 * @param out_means pointer to an array to store the means
 * @param out_sd pointer to an array to store the standard deviations
 *
 * @return 0 on success, -1 on invalid input, -2 on negative variance
 */

int em_means_sd(const double *data, int32_t rows, int32_t cols,
                double *out_means, double *out_sd);

