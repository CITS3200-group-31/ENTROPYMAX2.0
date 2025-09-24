#pragma once
#include <stdint.h>
#include <stddef.h>

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols, const char *const *colnames, const char *const *rownames);

// Returns 1 if native Parquet support is compiled in, 0 otherwise
int parquet_is_available(void);

// Write a Parquet file from an in-memory CSV buffer (UTF-8)
// Returns 0 on success, non-zero on failure
int parquet_write_from_csv_buffer(const char *path, const char *csv_buffer, size_t csv_size);

// Read a Parquet file into algorithm-friendly buffers.
// Expects a column named "Sample" for rownames. Optional columns "Latitude" and "Longitude".
// All other columns are treated as numeric bins (double).
// Allocates out buffers; caller must free using free() for arrays and for each string in rownames/colnames.
// Returns 0 on success, non-zero on failure.
int parquet_read_matrix_with_coords(const char *path,
                                    double **out_data, int *out_rows, int *out_cols,
                                    char ***out_rownames, char ***out_colnames,
                                    double **out_lat, double **out_lon);

