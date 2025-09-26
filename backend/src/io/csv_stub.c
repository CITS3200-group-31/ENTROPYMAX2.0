#include "csv.h"
#include <stdlib.h>

int csv_read_table(const char *path, csv_table_t *out) {
  (void)path; (void)out;
  return -1; // stub: not implemented yet
}

void csv_free_table(csv_table_t *t) {
  if (!t) return;
  free(t->data);
  if (t->colnames) {
    for (int32_t i = 0; i < t->cols; i++) free(t->colnames[i]);
    free(t->colnames);
  }
  if (t->rownames) {
    for (int32_t i = 0; i < t->rows; i++) free(t->rownames[i]);
    free(t->rownames);
  }
  t->data = NULL; t->colnames = NULL; t->rownames = NULL;
  t->rows = 0; t->cols = 0;
}


