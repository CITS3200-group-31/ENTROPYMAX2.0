#include "parquet.h"

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols,
                        const char *const *colnames, const char *const *rownames) {
  (void)path; (void)data; (void)rows; (void)cols; (void)colnames; (void)rownames;
  return -1; // stub: not implemented yet
}

// Stubbed compiled-only writer (returns non-zero so caller can handle/fallback)
#ifndef EM_HAVE_ARROW
int em_csv_to_parquet_with_gps(const char *algo_csv_path,
                               const char *gps_csv_path,
                               const char *out_parquet_path) {
  (void)algo_csv_path; (void)gps_csv_path; (void)out_parquet_path;
  return 1; // indicate unavailable
}
#endif


