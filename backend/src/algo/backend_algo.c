#include <stdint.h>
#include "algo.h"
#include "parquet.h"

int em_run_algo(const double *data, int32_t rows, int32_t cols, const char *const *colnames, const char *const *rownames, const char *parquet_out_path){
  // Placeholder: directly write input as output parquet once parquet_write_table exists
  return parquet_write_table(parquet_out_path, data, rows, cols, colnames, rownames);
}

