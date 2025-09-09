#include "logging.h"
#include <stdarg.h>

void log_message(log_level_t level, const char *fmt, ...) {
  (void)level; (void)fmt;
  // stub: swallow logs for now
  va_list args; va_start(args, fmt); va_end(args);
}


