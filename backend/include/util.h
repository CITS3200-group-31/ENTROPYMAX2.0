#pragma once
#include <stddef.h>
void *em_xmalloc(size_t n);
void *em_xcalloc(size_t n, size_t sz);
void em_free(void *p);

