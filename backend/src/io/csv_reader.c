#include <stdio.h>
#include <stdlib.h>
#include "csv.h"

int csv_read_table(const char *path, csv_table_t *out){
  // TODO: implement CSV parsing; placeholder returns error
  (void)path; (void)out; return -1;
}

void csv_free_table(csv_table_t *t){
  if(!t) return;
  free(t->data);
  if(t->colnames){ for(int i=0;i<t->cols;i++) free(t->colnames[i]); free(t->colnames);}
  if(t->rownames){ for(int i=0;i<t->rows;i++) free(t->rownames[i]); free(t->rownames);}
}

