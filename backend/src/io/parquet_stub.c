#include "parquet.h"
#include <stddef.h>

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols,
                        const char *const *colnames, const char *const *rownames) {
  (void)path; (void)data; (void)rows; (void)cols; (void)colnames; (void)rownames;
  return -1; // stub: not implemented yet
}

int parquet_is_available(void) { return 0; }

int parquet_write_from_csv_buffer(const char *path, const char *csv_buffer, size_t csv_size) {
  (void)path; (void)csv_buffer; (void)csv_size;
  return -1;
}

int parquet_read_matrix_with_coords(const char *path,
                                    double **out_data, int *out_rows, int *out_cols,
                                    char ***out_rownames, char ***out_colnames,
                                    double **out_lat, double **out_lon) {
  (void)path; (void)out_data; (void)out_rows; (void)out_cols; (void)out_rownames; (void)out_colnames; (void)out_lat; (void)out_lon;
  return -1;
}


