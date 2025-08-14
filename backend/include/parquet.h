#pragma once
#include <stdint.h>

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols, const char *const *colnames, const char *const *rownames);

