#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols, const char *const *colnames, const char *const *rownames);

// Compiled-only IO helpers (provided when Arrow/Parquet is enabled)
// Returns 0 on success.
int em_csv_to_parquet_with_gps(const char *algo_csv_path,
                               const char *gps_csv_path,
                               const char *out_parquet_path);

// Availability probe: returns 1 when Arrow/Parquet is compiled in, 0 otherwise.
int parquet_is_available(void);

#ifdef __cplusplus
}
#endif

