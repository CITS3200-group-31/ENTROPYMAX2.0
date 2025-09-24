#pragma once
#include <stdint.h>

typedef struct {
  double *data;           // row-major [rows * cols]
  char  **colnames;       // size cols
  char  **rownames;       // size rows
  int32_t rows;
  int32_t cols;
} csv_table_t;

int csv_read_table(const char *path, csv_table_t *out);
void csv_free_table(csv_table_t *t);

