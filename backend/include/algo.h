#pragma once
#include <stdint.h>

int em_run_algo(const double *data, int32_t rows, int32_t cols, const char *const *colnames, const char *const *rownames, const char *parquet_out_path);

