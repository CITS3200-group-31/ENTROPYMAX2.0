#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/**
 * @brief Reads a CSV file into a data matrix and row/column names.
 *
 * @param filename Path to the CSV file.
 * @param data Output pointer for the data matrix (allocated, rows*cols doubles).
 * @param rows Output: number of rows.
 * @param cols Output: number of columns.
 * @param rownames Output: array of row name strings (allocated).
 * @param colnames Output: array of column name strings (allocated).
 * @param sample_header_out Output: header string for the sample column (allocated).
 * @param raw_values_out Output: array of raw value strings (allocated, optional, can be NULL).
 * @return 0 on success, -1 on error.
 */
int read_csv(const char *filename, double **data, int *rows, int *cols,
             char ***rownames, char ***colnames,
             char **sample_header_out, char ***raw_values_out);