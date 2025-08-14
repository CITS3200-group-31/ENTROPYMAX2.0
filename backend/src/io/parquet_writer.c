#include "parquet.h"

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols, const char *const *colnames, const char *const *rownames){
  (void)path; (void)data; (void)rows; (void)cols; (void)colnames; (void)rownames;
  // TODO: implement Parquet writing via Arrow/Parquet C API or Python layer
  return -1;
}

