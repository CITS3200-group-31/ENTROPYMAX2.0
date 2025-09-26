#pragma once
#include <stddef.h>
// Unified backend error codes
typedef enum {
  EM_OK = 0,
  EM_ERR_INVALID_ARG = -1,
  EM_ERR_NOMEM = -2,
  EM_ERR_EMPTY_GROUP = -3,
  EM_ERR_INTERNAL = -4
} em_status_t;
void *em_xmalloc(size_t n);
void *em_xcalloc(size_t n, size_t sz);
void em_free(void *p);

