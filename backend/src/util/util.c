#include <stdlib.h>
#include "util.h"

void *em_xmalloc(size_t n){
  void *p = malloc(n);
  return p;
}
void *em_xcalloc(size_t n, size_t sz){
  void *p = calloc(n, sz);
  return p;
}
void em_free(void *p){
  free(p);
}

