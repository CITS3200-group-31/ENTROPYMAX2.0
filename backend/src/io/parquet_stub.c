#include "parquet.h"
#include <stddef.h>

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols,
                        const char *const *colnames, const char *const *rownames) {
  (void)path; (void)data; (void)rows; (void)cols; (void)colnames; (void)rownames;
  return -1; // stub: not implemented yet
}

int parquet_is_available(void) { return 0; }

// Stub for CSV->Parquet helper when Arrow/Parquet is not available
int em_csv_to_parquet_with_gps(const char *algo_csv_path,
                               const char *gps_csv_path,
                               const char *out_parquet_path) {
  (void)algo_csv_path; (void)gps_csv_path; (void)out_parquet_path;
  return -1;
}

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


// Stub for compiled postprocess helper referenced by run_entropymax.c when
// Arrow/Parquet C++ is not available. Returns non-zero to indicate no-op.
int em_csv_to_both_with_gps(const char *algo_csv_path,
                            const char *gps_csv_path,
                            const char *out_parquet_path,
                            const char *out_csv_frontend_path) {
  (void)algo_csv_path; (void)gps_csv_path; (void)out_parquet_path; (void)out_csv_frontend_path;
  return -1;
}


